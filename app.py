from flask import Flask, render_template, request, jsonify
from email import policy
from email.parser import BytesParser, Parser
from pathlib import Path
from urllib.parse import urlparse
import base64, datetime, ipaddress, os, re, socket, ssl
import requests, whois

from detector import check_email_message, check_phone_message, urls as extract_urls, normalize_domain, domain_from_url
from utils import save_result

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)
app = Flask(__name__, template_folder="templates", static_folder="static")
URL_LIMIT = 3
SCAN_MODE = "Standard"
VT_API = "https://www.virustotal.com/api/v3"


def jdata():
    return request.get_json(silent=True) or {}



def scan_source_value():
    raw = (request.form.get("scan_source") or jdata().get("scan_source") or "computer").lower().strip()
    return "phone" if raw in {"phone","mobile"} else "computer"



FOOTER_URL_WORDS = (
    "unsubscribe","privacy","cookie","cookies","legal","terms","site-information",
    "about-site-provider","legal-disclaimer","ats-privacy-statement","legal-entities",
    "ethics-business-conduct","office-locations","member-firms","corporate-governance",
    "corporategovernance","network-structure","structure"
)
ACTION_URL_WORDS = (
    "login","signin","sign-in","verify","account","activate","confirm","reset",
    "password","portal","candidate","apply","application","jobs","careers","token","auth","sso"
)


def keep_href(href, label=""):
    low = ((href or "") + " " + (label or "")).lower()
    if not low.strip().startswith(("http://", "https://")):
        return False
    if any(w in low for w in FOOTER_URL_WORDS):
        return False
    return True


def html_to_scan_text(html):
    hrefs = []
    for m in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html or "", flags=re.I|re.S):
        href = m.group(1) or ""
        label = re.sub(r"<[^>]+>", " ", m.group(2) or "")
        if keep_href(href, label):
            hrefs.append(href)
    visible = re.sub(r"<[^>]+>", " ", html or "")
    return (visible + "\n" + "\n".join(dict.fromkeys(hrefs))).strip()

def parse_eml(raw: bytes):
    msg = BytesParser(policy=policy.default).parsebytes(raw or b"")
    headers = {k: msg.get(k, "") or "" for k in ["From","Reply-To","To","Subject","Date","Authentication-Results","ARC-Authentication-Results","Received-SPF","DKIM-Signature"]}
    text, html, attachments = [], [], []
    for part in msg.walk():
        if part.is_multipart():
            continue
        ctype = (part.get_content_type() or "").lower()
        disp = (part.get("Content-Disposition") or "").lower()
        fname = part.get_filename()
        if fname or "attachment" in disp or ctype.startswith(("image/","application/")):
            attachments.append(fname or ctype or "attachment")
            continue
        try: content = part.get_content()
        except Exception:
            payload = part.get_payload(decode=True) or b""
            content = payload.decode(part.get_content_charset() or "utf-8", "ignore")
        if ctype == "text/html": html.append(content)
        else: text.append(content)
    body = "\n".join(text).strip()
    if html:
        h = "\n".join(html)
        body = (body + "\n" + html_to_scan_text(h)).strip()
    return {"headers": headers, "body": body, "attachments": attachments}


def parse_email_text(raw: str):
    msg = Parser(policy=policy.default).parsestr(raw or "")
    headers = {k: msg.get(k, "") or "" for k in ["From","Reply-To","To","Subject","Date","Authentication-Results","ARC-Authentication-Results","Received-SPF","DKIM-Signature"]}
    body = msg.get_body(preferencelist=("plain","html"))
    try: body_text = body.get_content() if body else raw
    except Exception: body_text = raw
    return {"headers": headers, "body": body_text or raw or "", "attachments": []}


def meta(parsed, phone=False):
    h = parsed.get("headers", {}) if parsed else {}
    if phone:
        return {"from":"", "reply_to":"", "subject":"Copied phone message"}
    return {"from": h.get("From", ""), "reply_to": h.get("Reply-To", ""), "subject": h.get("Subject", "")}


def private_ip(ip):
    try:
        x = ipaddress.ip_address(ip)
        return x.is_private or x.is_loopback or x.is_link_local or x.is_reserved or x.is_multicast or x.is_unspecified
    except Exception:
        return True


def safe_host(host):
    try:
        ips = sorted({i[4][0] for i in socket.getaddrinfo(host, None)})
        return not any(private_ip(ip) for ip in ips)
    except Exception:
        return True


def redirects(url, timeout=8):
    try:
        r = requests.head(url, allow_redirects=True, timeout=timeout)
        return [x.url for x in r.history] + [r.url], r.url, r.status_code
    except Exception:
        try:
            r = requests.get(url, allow_redirects=True, timeout=timeout, stream=True)
            return [x.url for x in r.history] + [r.url], r.url, r.status_code
        except Exception:
            return [], url, None


def whois_brief(host):
    try:
        w = whois.whois(host)
        created, expires = w.creation_date, w.expiration_date
        if isinstance(created, list): created = min(created)
        if isinstance(expires, list): expires = max(expires)
        age = (datetime.datetime.utcnow() - created.replace(tzinfo=None)).days if isinstance(created, datetime.datetime) else None
        return {"registrar": w.registrar, "creation_date": str(created) if created else None, "expiration_date": str(expires) if expires else None, "age_days": age}
    except Exception as e:
        return {"error": str(e)}


def tls_brief(host):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=7) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as s:
                cert = s.getpeercert()
        issuer = dict(x[0] for x in cert.get("issuer", []))
        subject = dict(x[0] for x in cert.get("subject", []))
        return {"issuer": issuer.get("organizationName") or issuer.get("O") or "", "subject": subject.get("commonName") or "", "valid_from": cert.get("notBefore") or "", "valid_to": cert.get("notAfter") or ""}
    except Exception as e:
        return {"error": f"{e.__class__.__name__}: {e}"}


def vt_id(url):
    return base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")


def vt_report(url, key):
    key = (key or "").strip()
    if not key:
        return {"provider":"VirusTotal", "available":False, "note":"Not available — API key not provided"}
    headers = {"x-apikey": key}
    try:
        r = requests.get(f"{VT_API}/urls/{vt_id(url)}", headers=headers, timeout=8)
        if r.status_code == 200:
            attr = r.json().get("data", {}).get("attributes", {})
            return {"provider":"VirusTotal", "available":True, "source":"cache", "stats": attr.get("last_analysis_stats", {})}
        r = requests.post(f"{VT_API}/urls", headers=headers, data={"url": url}, timeout=8)
        if r.status_code in (200,201):
            return {"provider":"VirusTotal", "available":True, "source":"pending", "note":"Pending — submitted to VirusTotal"}
        return {"provider":"VirusTotal", "available":False, "note":f"VT status {r.status_code}"}
    except Exception as e:
        return {"provider":"VirusTotal", "available":False, "note":str(e)}


def url_insight(url, vt_key):
    out = {"source_url": url}
    host0 = normalize_domain(domain_from_url(url))
    if host0 and not safe_host(host0):
        out.update({"final_url": None, "redirect_chain": [], "whois": {}, "tls": {}, "threat_intel": vt_report(url, vt_key), "verdict":"Blocked", "confidence":"High"})
        return out
    chain, final, status = redirects(url)
    host = normalize_domain(domain_from_url(final or url))
    out.update({"final_url": final, "redirect_chain": chain, "status": status, "host": host})
    out["whois"] = whois_brief(host) if host else {}
    out["tls"] = tls_brief(host) if host and (final or url).lower().startswith("https://") else {}
    out["threat_intel"] = vt_report(final or url, vt_key)
    stats = out.get("threat_intel", {}).get("stats", {}) or {}
    if stats.get("malicious", 0) > 0:
        out["verdict"], out["confidence"] = "Likely phishing", "High"
    elif stats.get("suspicious", 0) > 0 or (url or "").lower().startswith("http://"):
        out["verdict"], out["confidence"] = "Suspicious", "Medium"
    else:
        out["verdict"], out["confidence"] = "Likely safe", "High"
    return out



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/check", methods=["POST"])
def api_check():
    source = scan_source_value(); vt_key = request.form.get("vt_api_key") or jdata().get("vt_api_key") or ""
    if "eml_file" in request.files:
        parsed = parse_eml(request.files["eml_file"].read())
        res = check_email_message(parsed)
        res.update({"scan_source":"Computer / EML File", "scan_mode":SCAN_MODE, "meta":meta(parsed)})
        text = parsed.get("body", "")
        input_type = "eml_file"
    else:
        text = request.form.get("text") or jdata().get("text", "") or ""
        if source == "phone":
            res = check_phone_message(text)
            res.update({"scan_source":"Phone / Copied Message", "scan_mode":SCAN_MODE, "meta":meta({}, phone=True)})
            input_type = "phone_copied_message"
        else:
            parsed = parse_email_text(text)
            res = check_email_message(parsed)
            res.update({"scan_source":"Computer / Email", "scan_mode":SCAN_MODE, "meta":meta(parsed)})
            input_type = "pasted_email"
    found = extract_urls(text)[:URL_LIMIT]
    res["insights"] = [url_insight(u, vt_key) for u in found]
    res["saved_to"] = save_result({"input_type": input_type, "result": res})
    return jsonify(res)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
