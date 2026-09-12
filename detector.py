import csv, re, requests
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse
BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
COMPANIES_FILE = DATA / "companies.csv"
BLACKLIST_FILE = DATA / "blacklist_emails.txt"
TOP_FILE = DATA / "top_domains.txt"
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
URL_RE = re.compile(r"https?://[^\s'\"<>]+", re.I)
FREE_MAIL = {"gmail.com","yahoo.com","hotmail.com","outlook.com","live.com","icloud.com","proton.me","protonmail.com","aol.com"}
SHORTENERS = {"bit.ly","tinyurl.com","t.co","goo.gl","ow.ly","is.gd","cutt.ly","rb.gy","lnkd.in"}
TRUSTED_AUTH = {"accounts.google.com","login.microsoftonline.com","outlook.office.com","appleid.apple.com","okta.com","auth0.com"}
TRUSTED_SAAS = {"myworkday.com","workday.com","myworkdayjobs.com","greenhouse.io","lever.co","smartrecruiters.com","sendgrid.net","mailchimp.com"}
IGNORE_URL_WORDS = (
    "unsubscribe","privacy","cookie","cookies","legal","terms","preferences","viewonline",
    "site-information","about-site-provider","legal-disclaimer","ats-privacy-statement",
    "legal-entities","ethics-business-conduct","office-locations","member-firms",
    "corporate-governance","corporategovernance","network-structure","structure"
)
ACTION_URL_WORDS = (
    "login","signin","sign-in","verify","account","activate","confirm","reset","password",
    "portal","candidate","apply","application","jobs","careers","token","auth","sso"
)
URGENT_WORDS = {"urgent","immediately","expire","expires","expired","limited","suspended","locked","blocked","warning","alert","final","now","today","closure","avoid","عاجل","فورا","ينتهي","انتهت","ايقاف","تحذير"}
ACCOUNT_WORDS = {"login","signin","verify","verification","password","otp","code","token","account","payment","invoice","confirm","reset","activate","bank","banking","card","details","update","access","restore","secure","information","تسجيل","دخول","تحقق","تأكيد","كود","حساب","دفع"}
FINANCE_WORDS = {"bank","banking","card","payment","wallet","invoice","paypal","amazon","apple","microsoft","google"}
GENERIC_TERMS = {
    "account","login","verify","email","mail","security","team","service","support","data",
    "current","about","activity","customer","click","here","info","admin","help","portal",
    "mobile","settings","update","events","play","officeapps","live","edge","private"
}
def normalize_domain(host):
    host = (host or "").lower().strip().rstrip(".")
    return host[4:] if host.startswith("www.") else host
def domain_from_url(url):
    try:
        return normalize_domain(urlparse(url).hostname or "")
    except Exception:
        return ""
def domain_from_email(text):
    m = EMAIL_RE.search(text or "")
    return normalize_domain(m.group(0).split("@", 1)[1]) if m else ""
def email_from_text(text):
    m = EMAIL_RE.search(text or "")
    return m.group(0).lower() if m else ""
def regdom(host):
    host = normalize_domain(host)
    if not host:
        return ""
    parts = [p for p in host.split(".") if p]
    if len(parts) <= 2:
        return host
    sld = {"co","com","net","org","gov","edu","ac"}
    if len(parts[-1]) == 2 and parts[-2] in sld and len(parts) >= 3:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])
def brand_part(domain):
    return regdom(domain).split(".", 1)[0]
def urls(text):
    out, seen = [], set()
    for u in URL_RE.findall(text or ""):
        u = u.strip().strip(".,;:!?)'\"<>[]{}")
        low = u.lower()
        if any(w in low for w in IGNORE_URL_WORDS):
            continue
        host = domain_from_url(u)
        path = (urlparse(u).path or "/").rstrip("/").lower() or "/"
        key = (host, path)
        if key not in seen:
            seen.add(key)
            out.append(u)
    out.sort(key=lambda u: (any(w in u.lower() for w in ACTION_URL_WORDS), u.lower().startswith("https://")), reverse=True)
    return out
def split_aliases(value):
    return [normalize_domain(a.strip()) for a in re.split(r"[,|;]", value or "") if a.strip()]
def load_companies():
    rows = []
    if not COMPANIES_FILE.exists():
        return rows
    with open(COMPANIES_FILE, encoding="utf-8-sig", errors="ignore", newline="") as f:
        for r in csv.DictReader(f):
            domain = normalize_domain(r.get("domain", ""))
            if not domain:
                continue
            aliases = [a for a in split_aliases(r.get("aliases", "")) if a and a != domain]
            name = (r.get("company") or "").strip()
            rows.append({"company": name, "domain": domain, "aliases": aliases, "category": (r.get("category") or "").strip()})
    return rows
def load_set(path):
    if not Path(path).exists():
        return set()
    return {normalize_domain(x.strip()) for x in open(path, encoding="utf-8", errors="ignore") if x.strip()}
COMPANIES = load_companies()
BLACKLIST = load_set(BLACKLIST_FILE)
TOP_DOMAINS = load_set(TOP_FILE)
def similarity(a, b):
    return SequenceMatcher(None, a or "", b or "").ratio()
def alias_matches(host, alias):
    host, alias = normalize_domain(host), normalize_domain(alias)
    if not host or not alias:
        return False
    return host == alias or regdom(host) == regdom(alias) or host.endswith("." + alias)
def match_company(host):
    host = normalize_domain(host)
    rhost = regdom(host)
    best, score = None, 0.0
    for c in COMPANIES:
        cdom = normalize_domain(c.get("domain"))
        rcomp = regdom(cdom)
        aliases = [normalize_domain(a) for a in c.get("aliases", [])]
        if host == cdom or rhost == rcomp or any(alias_matches(host, a) for a in aliases):
            return c, 1.0
        candidates = [similarity(host, cdom), similarity(rhost, rcomp)]
        candidates += [similarity(rhost, regdom(a)) for a in aliases[:30]]
        s = max(candidates) if candidates else 0
        if s > score:
            best, score = c, s
    return (best, score) if best and score >= 0.82 else (None, 0.0)
def final_host(url, timeout=4):
    try:
        r = requests.head(url, allow_redirects=True, timeout=timeout)
        return domain_from_url(r.url) or domain_from_url(url)
    except Exception:
        try:
            r = requests.get(url, allow_redirects=True, timeout=timeout, stream=True)
            return domain_from_url(r.url) or domain_from_url(url)
        except Exception:
            return domain_from_url(url)
def text_hits(text, words):
    low = (text or "").lower()
    return sorted({w for w in words if re.search(r"(?<![a-z0-9])" + re.escape(w.lower()) + r"(?![a-z0-9])", low)})
def mentioned_companies(text):
    low = (text or "").lower()
    found = []
    tokens = set(re.findall(r"[a-z0-9][a-z0-9\-]{2,}", low))
    for c in COMPANIES:
        dom_brand = brand_part(c.get("domain", ""))
        name = (c.get("company") or "").lower().strip()
        terms = []
        if len(dom_brand) >= 4 and dom_brand not in GENERIC_TERMS:
            terms.append(dom_brand)
        if len(name) >= 4 and name not in GENERIC_TERMS:
            terms.append(name)
        for a in c.get("aliases", [])[:20]:
            b = brand_part(a)
            if len(b) >= 4 and b not in GENERIC_TERMS:
                terms.append(b)
        if any((" " in t and t in low) or (t in tokens) for t in set(terms)):
            found.append(c)
    return found[:6]
def finish(res):
    total = int(res.get("score", 0))
    res["total_score"] = total
    if total >= 80 or (total >= 65 and res.get("hard_signal")):
        verdict = "Likely phishing"
    elif total >= 35:
        verdict = "Suspicious"
    else:
        verdict = "Likely safe"
    res["verdict"] = verdict
    res["confidence"] = "High" if verdict == "Likely phishing" or abs(total) >= 60 else ("Medium" if abs(total) >= 25 else "Low")
    return res
def common_content_checks(res, text, mode_label="Message"):
    content = text or ""
    urgent = text_hits(content, URGENT_WORDS)
    account = text_hits(content, ACCOUNT_WORDS)
    finance = text_hits(content, FINANCE_WORDS)
    if urgent and account:
        res["score"] += 25
        res["reasons"].append(f"{mode_label} combines urgency/threat language with account or verification wording: " + ", ".join((urgent + account)[:8]))
    if finance and account:
        res["score"] += 12
        res["reasons"].append(f"{mode_label} contains brand/payment/account context")
    comps = mentioned_companies(EMAIL_RE.sub(" ", content))
    if comps:
        names = []
        for c in comps:
            n = c.get("company") or brand_part(c.get("domain"))
            if n and n.lower() not in GENERIC_TERMS and n not in names:
                names.append(n)
        if names:
            res["reasons"].append("Message mentions known company context: " + ", ".join(names[:5]))
    return urgent, account, finance
def score_links(res, raw_urls, sender_reg="", good_auth=False, phone=False):
    unknown_links = known_links = 0
    trusted_saas_sender = sender_reg in TRUSTED_SAAS
    for u in raw_urls[:6 if phone else 4]:
        host = final_host(u)
        rhost = regdom(host)
        score = 0
        comp, comp_score = match_company(host)
        if u.lower().startswith("http://"):
            score += 12 if phone else 8
            res["reasons"].append(("Phone link" if phone else "Link") + f" uses plain HTTP: {u}")
        if rhost in SHORTENERS:
            score += 25 if phone else 18
            res["reasons"].append(("Phone link" if phone else "URL") + f" shortener used: {rhost}")
        if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host):
            score += 45
            res["hard_signal"] = True
            res["reasons"].append("Link uses raw IP address")
        if sender_reg and rhost == sender_reg:
            known_links += 1
            res["reasons"].append(f"Link final host {host} matches sender domain family")
        elif comp and comp_score == 1.0 and regdom(comp.get("domain")) == rhost:
            known_links += 1
            score -= 10 if phone else 0
            res["reasons"].append(f"Link belongs to known company domain: {host} ({comp['company']})")
        elif rhost in TRUSTED_SAAS and (phone or trusted_saas_sender or good_auth):
            known_links += 1
            res["reasons"].append(f"Expected SaaS/client link {host} — not penalized")
        elif host in TRUSTED_AUTH or rhost in TOP_DOMAINS:
            known_links += 1
            score -= 5
            res["reasons"].append(f"Link is trusted/popular: {host}")
        else:
            unknown_links += 1
            score += 28 if phone else 26
            res["reasons"].append(("Phone link" if phone else "Link") + f" domain is not found in trusted lists: {host}")
        if len(u) > 240:
            score += 5
        score = max(-20, min(70 if phone else 30, score))
        res["score"] += score
        res["urls"].append({"url": u, "final_host": host, "score": score})
    return unknown_links, known_links
def check_email_message(parsed):
    h = parsed.get("headers", {}) or {}
    body = parsed.get("body", "") or ""
    from_h, reply, subject = h.get("From", ""), h.get("Reply-To", ""), h.get("Subject", "")
    auth = (h.get("Authentication-Results", "") or h.get("ARC-Authentication-Results", "") or h.get("Received-SPF", "")).lower()
    sender_email = email_from_text(from_h)
    sender_dom = domain_from_email(from_h)
    sender_reg = regdom(sender_dom)
    res = {"score": 0, "reasons": [], "matches": [], "urls": []}
    if sender_email in BLACKLIST or sender_dom in BLACKLIST:
        res["score"] += 120
        res["hard_signal"] = True
        res["reasons"].append("Sender email/domain is on local blacklist")
    company, _ = match_company(sender_dom)
    free_sender = sender_reg in FREE_MAIL
    if sender_dom:
        if free_sender:
            res["score"] += 70
            res["free_sender"] = True
            res["reasons"].append(f"Sender uses a personal/free mailbox provider ({sender_dom})")
        elif company:
            res["score"] -= 5
            res["matches"].append({"type": "sender_domain", "company": company["company"], "company_domain": company["domain"]})
            res["reasons"].append(f"Sender domain {sender_dom} recognized as a known company")
        elif sender_dom in TOP_DOMAINS:
            res["score"] -= 10
            res["reasons"].append(f"Sender domain {sender_dom} is in popular list")
        else:
            res["reasons"].append(f"Sender domain {sender_dom} not in known lists → neutral signal")
    good_auth = any(x in auth for x in ("spf=pass","dkim=pass","dmarc=pass"))
    bad_auth = any(x in auth for x in ("spf=fail","dkim=fail","dmarc=fail"))
    if good_auth and not free_sender:
        res["score"] -= 15
        res["reasons"].append("SPF/DKIM pass → reduces suspicion")
    elif good_auth:
        res["reasons"].append("SPF/DKIM pass for free mailbox provider → mailbox trust only")
    elif bad_auth:
        res["score"] += 40
        res["reasons"].append("SPF/DKIM/DMARC fail → raises suspicion")
    content = " ".join([subject or "", body or ""])
    urgent, account, finance = common_content_checks(res, content, "Email text")
    raw_urls = urls(body)
    has_sender_context = bool(sender_dom or good_auth or bad_auth)
    if raw_urls and not has_sender_context:
        res["score"] += 16
        res["reasons"].append("No trusted email headers/sender context found in pasted message")
    unknown, known = score_links(res, raw_urls, sender_reg, good_auth, phone=False)
    if unknown and (urgent or account):
        res["score"] += 28
        res["hard_signal"] = True
        res["reasons"].append("Unknown link combined with urgency/account language")
    if finance and unknown:
        res["score"] += 18
        res["hard_signal"] = True
        res["reasons"].append("Brand/payment context points to an unknown domain")
    if known and not unknown and good_auth and res["score"] > 20:
        res["score"] = 20
        res["reasons"].append("Authenticated known-company/SaaS flow kept low risk")
    if free_sender and raw_urls:
        res["score"] += 15
        res["reasons"].append("Unknown free-email sender contains link(s) → higher phishing risk")
    if res.get("free_sender") and res["score"] < 35:
        res["score"] = 35
        res["reasons"].append("Free-mail sender guardrail: minimum verdict is Suspicious")
    return finish(res)
def check_phone_message(text):
    text = text or ""
    res = {"score": 0, "reasons": [], "matches": [], "urls": [], "phone_mode": True, "scan_source": "Phone / Copied Message"}
    for em in sorted(set(e.lower() for e in EMAIL_RE.findall(text)))[:5]:
        dom = em.split("@", 1)[1]
        comp, _ = match_company(dom)
        if regdom(dom) in FREE_MAIL:
            res["score"] += 30
            res["reasons"].append(f"Copied phone text contains a free/personal email address: {em}")
        elif comp:
            res["score"] -= 5
            res["reasons"].append(f"Copied phone text contains email from known company domain: {em}")
        else:
            res["score"] += 22
            res["reasons"].append(f"Copied phone text contains email from unknown domain: {dom}")
    urgent, account, finance = common_content_checks(res, text, "Mobile text")
    raw_urls = urls(text)
    unknown, known = score_links(res, raw_urls, phone=True)
    if unknown and (urgent or account):
        res["score"] += 28
        res["hard_signal"] = True
        res["reasons"].append("Unknown phone link combined with urgency/account language")
    if finance and unknown:
        res["score"] += 16
        res["hard_signal"] = True
        res["reasons"].append("Brand/payment context points to an unknown phone link")
    if known and not unknown and not res.get("hard_signal"):
        if urgent:
            res["reasons"].append("Urgency words found but ignored because the link belongs to a known company")
        if res["score"] > 20:
            res["score"] = 20
    if not raw_urls:
        res["reasons"].append("No URLs found in copied phone text")
    return finish(res)
