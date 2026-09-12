const $ = id => document.getElementById(id);
const val = name => document.querySelector(`input[name="${name}"]:checked`)?.value;
const esc = v => String(v ?? "—").replace(/[&<>"']/g, m => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[m]));

const I18N = {
  ar: {
    nav_home:"الرئيسية", nav_about:"عن المشروع", nav_features:"المميزات", nav_scan:"ابدأ الفحص",
    eyebrow:"مشروع تخرج / Cybersecurity / SOC",
    hero_title:"phishior لفحص الإيميلات والروابط ضد التصيد",
    hero_text:"أداة خفيفة بتحلل ملف EML أو نص منسوخ من الموبايل أو رابط مباشر باستخدام مؤشرات أمنية مثل المرسل، أهم 3 روابط، WHOIS، TLS، و VirusTotal اختياريًا بدون عرض صور أو تفاصيل زائدة.",
    start_now:"🚀 ابدأ الفحص الآن", explore:"اعرف المميزات",
    about_title:"عن المشروع",
    about_text:"phishior مشروع ويب بلغة Python/Flask يساعد المستخدم على اكتشاف الرسائل والروابط المشبوهة قبل التفاعل معها، مع تقرير مختصر وسهل القراءة.",
    c1t:"تحليل الإيميل", c1p:"يقرأ بيانات المرسل والعنوان و Reply-To ونتائج المصادقة من ملف EML أو النص الخام.",
    c2t:"تحليل الروابط", c2p:"يفحص أهم 3 روابط فقط بعد فلترة روابط الفوتر والقانونيات، ويعرض الرابط النهائي و WHOIS و TLS.",
    c3t:"فحص الموبايل", c3p:"يفحص الرسائل المنسوخة من الهاتف بدون تطبيق قواعد هيدرز الإيميل عليها.",
    features_title:"المميزات الأساسية", features_text:"يحافظ على دقة الفحص الجديدة مع واجهة قريبة من الشكل القديم.",
    f1t:"VirusTotal اختياري", f1p:"يعمل فقط لو المستخدم أدخل API Key، ويظهر كعامل تأكيد إضافي لا يغير التقييم الأساسي.",
    f2t:"Trusted Domains", f2p:"تُستخدم الدومينات الموثوقة والقائمة السوداء داخليًا لتقليل الإنذارات الخاطئة بدون إتاحة التعديل للمستخدم العام.",
    f3t:"Reasons & Score", f3p:"يعرض الحكم والنقاط والأسباب بدون JSON خام أو تفاصيل زائدة.",
    how_title:"طريقة العمل", how_text:"خطوات بسيطة من رفع الإيميل حتى ظهور النتيجة.",
    s1t:"ارفع أو الصق", s1p:"ارفع ملف .eml أو الصق نص الرسالة أو الرابط.",
    s2t:"اختر المصدر", s2p:"Computer للإيميل الكامل أو Phone للرسائل المنسوخة.",
    s3p:"اضغط فحص وانتظر التقرير.", s4t:"راجع النتيجة", s4p:"شوف الحكم، النقاط، الروابط، والأسباب.",
    scan_title:"ابدأ الفحص", scan_text:"استخدم هذا الجزء لفحص رابط مباشر، نص إيميل، رسالة موبايل، أو ملف EML كامل.",
    settings:"إعداد الفحص", source_label:"مصدر الرسالة", recommended:"Recommended", advanced:"Advanced Analysis", quick:"Quick Scan",
    computer_desc:"Full email scan using headers, sender details, links, and EML rules.",
    phone_desc:"Copied message scan using visible text, links, brand context, and risk words.",
    source_help:"Computer = Advanced Analysis • Phone = Quick Scan للنص المنسوخ والروابط فقط.",
    optional:"(اختياري، لا يتم حفظه في ملف)", scan_type_label:"نوع الفحص", standard_hint:"Standard Scan — أهم 3 روابط + VirusTotal اختياري",
    paste_label:"ألصق نص الإيميل الكامل أو الرابط:", upload_or_paste:"ارفع EML أو الصق النص", scan_btn:"فحص / Scan Now", clear_btn:"مسح", wait:"جارٍ الفحص... برجاء الانتظار",
    verdict:"Verdict:", score:"Total score:", confidence:"Confidence:", scan_source:"Scan source:", scan_mode:"Scan mode:", saved_file:"Saved file:",
    sender_info:"Sender Information", urls_found:"URLs Found in Email", reasons_title:"Reasons and Ratings",
    contact_text:"معلومات صاحب المشروع والتواصل.",
    safe:"Likely Safe", phish:"Likely Phishing", suspicious:"Suspicious", delete:"Delete", noReasons:"لا أسباب إضافية مُسجّلة",
    empty:"ارفع ملف EML أو الصق رسالة/رابط الأول", scanning:"جارٍ الفحص...", server:"خطأ في السيرفر", domainFirst:"أدخل الدومين الأول"
  },
  en: {
    nav_home:"Home", nav_about:"About", nav_features:"Features", nav_scan:"Start Scan",
    eyebrow:"Graduation Project / Cybersecurity / SOC",
    hero_title:"phishior for phishing email and URL detection",
    hero_text:"A lightweight tool that analyzes EML files, copied phone messages, or direct URLs using sender data, the top 3 important URLs, WHOIS, TLS, and optional VirusTotal without screenshots or noisy details.",
    start_now:"🚀 Start Scan Now", explore:"Explore Features",
    about_title:"About",
    about_text:"phishior is a Python/Flask web project that helps users detect suspicious emails and URLs before interacting with them, using a clean and readable report.",
    c1t:"Email Analysis", c1p:"Reads sender, subject, Reply-To, and authentication data from EML files or raw email text.",
    c2t:"URL Analysis", c2p:"Scans only the top 3 important URLs after filtering footer/legal links, then shows final URL, WHOIS, and TLS.",
    c3t:"Phone Scan", c3p:"Scans copied phone messages without applying email-header rules.",
    features_title:"Core Features", features_text:"Keeps the new scanning accuracy with a UI close to the old design.",
    f1t:"Optional VirusTotal", f1p:"Runs only when the user enters an API key and acts as extra confirmation without changing the main score.",
    f2t:"Trusted Domains", f2p:"Trusted domains and blacklists are used internally to reduce false positives without exposing public editing controls.",
    f3t:"Reasons & Score", f3p:"Shows verdict, score, and reasons without raw JSON or noisy details.",
    how_title:"How It Works", how_text:"Simple steps from upload to result.",
    s1t:"Upload or Paste", s1p:"Upload an .eml file or paste the message or URL.",
    s2t:"Choose Source", s2p:"Use Computer for full email analysis or Phone for copied messages.",
    s3p:"Click scan and wait for the report.", s4t:"Review Result", s4p:"Check verdict, score, URLs, and reasons.",
    scan_title:"Start Scan", scan_text:"Scan a direct URL, email text, phone message, or full EML file.",
    settings:"Scan Settings", source_label:"Message Source", recommended:"Recommended", advanced:"Advanced Analysis", quick:"Quick Scan",
    computer_desc:"Full email scan using headers, sender details, links, and EML rules.",
    phone_desc:"Copied message scan using visible text, links, brand context, and risk words.",
    source_help:"Computer = Advanced Analysis • Phone = Quick Scan for copied text and links only.",
    optional:"(Optional, not saved to a file)", scan_type_label:"Scan Type", standard_hint:"Standard Scan — Top 3 important URLs + optional VirusTotal",
    paste_label:"Paste full email text or URL:", upload_or_paste:"Upload EML or paste text", scan_btn:"Scan Now", clear_btn:"Clear", wait:"Scanning... please wait",
    verdict:"Verdict:", score:"Total score:", confidence:"Confidence:", scan_source:"Scan source:", scan_mode:"Scan mode:", saved_file:"Saved file:",
    sender_info:"Sender Information", urls_found:"URLs Found in Email", reasons_title:"Reasons and Ratings",
    contact_text:"Project owner and contact information.",
    safe:"Likely Safe", phish:"Likely Phishing", suspicious:"Suspicious", delete:"Delete", noReasons:"No additional reasons recorded",
    empty:"Please upload an EML file or paste a message/URL first.", scanning:"Scanning...", server:"Server error", domainFirst:"Enter the domain first"
  }
};

const PH = {
  ar: { vt:"ضع مفتاح VirusTotal هنا للتأكد الإضافي", msg:"https://example.com أو الصق الرسالة هنا" },
  en: { vt:"Paste your VirusTotal API key for extra confirmation", msg:"https://example.com or paste the message here" }
};

let lang = localStorage.getItem("phishior_lang") || "ar";
const T = key => (I18N[lang] || I18N.ar)[key] || key;

function applyLang(nextLang){
  lang = nextLang || lang;
  localStorage.setItem("phishior_lang", lang);
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  document.body.dir = document.documentElement.dir;
  document.querySelectorAll("[data-i18n]").forEach(el => el.textContent = T(el.dataset.i18n));
  document.querySelectorAll("[data-ph]").forEach(el => el.placeholder = (PH[lang] || PH.ar)[el.dataset.ph] || el.placeholder);
  $("langBtn").textContent = lang === "ar" ? "EN" : "AR";
}
function toggleLang(){ applyLang(lang === "ar" ? "en" : "ar"); }

function setText(id, value){ const el = $(id); if(el) el.textContent = value === 0 ? 0 : (value || "—"); }
function setLoading(on){
  $("btnScan").disabled = on;
  $("btnClear").disabled = on;
  $("scanLoader").style.display = on ? "inline-block" : "none";
  $("scanFeedback").classList.toggle("active", on);
  $("scanText").textContent = on ? T("scanning") : T("scan_btn");
  $("scanStatus").textContent = T("wait");
}
function clearAll(){
  ["msg", "emlfile"].forEach(id => { $(id).value = ""; });
  $("result_area").style.display = "none";
  $("scanFeedback").classList.remove("active");
}

function verdictBadge(v){
  let cls = "ok", txt = T("safe");
  v = (v || "").toLowerCase();
  if(v.includes("phish")){ cls = "bad"; txt = T("phish"); }
  else if(v.includes("suspicious")){ cls = "warn"; txt = T("suspicious"); }
  $("verdict_badge").innerHTML = `<span class="badge ${cls}">${txt}</span>`;
  setText("summary_verdict", txt);
}
function vtLine(ti){
  if(!ti) return "Not available";
  if(ti.available){
    const s = ti.stats || {};
    if(ti.source === "pending") return ti.note || "Pending — submitted to VirusTotal";
    return `${ti.source || "Reviewed"} — malicious:${s.malicious || 0} suspicious:${s.suspicious || 0} harmless:${s.harmless || 0} undetected:${s.undetected || 0}`;
  }
  return `Not available${ti.note ? " — " + ti.note : ""}`;
}
function chainHtml(arr){
  return Array.isArray(arr) && arr.length
    ? `<ol class="ltr">${arr.map(u => `<li>${esc(u)}</li>`).join("")}</ol>`
    : "—";
}
function insightHtml(ins, i){
  const w = ins.whois || {}, tls = ins.tls || {}, ti = ins.threat_intel || {};
  return `<div class="url-card">
    <h4>#${i + 1}</h4>
    <div class="kv"><span class="k">Card verdict:</span><b>${esc(ins.verdict || "Likely safe")}</b></div>
    <div class="kv"><span class="k">Confidence:</span>${esc(ins.confidence || "High")}</div>
    <div class="kv"><span class="k">Source URL:</span><span class="ltr">${esc(ins.source_url)}</span></div>
    <div class="kv"><span class="k">Final URL:</span><span class="ltr">${esc(ins.final_url)}</span></div>
    <div class="kv"><span class="k">Redirect Chain:</span>${chainHtml(ins.redirect_chain)}</div>
    <div class="sep"></div><b>WHOIS</b>
    <div class="kv"><span class="k">Registrar:</span>${esc(w.registrar)}</div>
    <div class="kv"><span class="k">Created:</span>${esc(w.creation_date)}</div>
    <div class="kv"><span class="k">Expires:</span>${esc(w.expiration_date)}</div>
    <div class="kv"><span class="k">Age (days):</span>${esc(w.age_days)}</div>
    <div class="sep"></div><b>TLS</b>
    <div class="kv"><span class="k">Issuer:</span>${esc(tls.issuer || (tls.error ? "Error: " + tls.error : ""))}</div>
    <div class="kv"><span class="k">Subject:</span>${esc(tls.subject)}</div>
    <div class="kv"><span class="k">Valid:</span>${esc(tls.valid_from)} → ${esc(tls.valid_to)}</div>
    <div class="sep"></div><b>VirusTotal</b>
    <div class="kv">${esc(vtLine(ti))}</div>
  </div>`;
}

async function smartScan(){
  const file = $("emlfile").files[0];
  const text = $("msg").value.trim();
  if(!file && !text) return alert(T("empty"));
  setLoading(true);
  try{
    const fd = new FormData();
    fd.append("type", "email");
    fd.append("scan_source", val("scan_source") || "computer");
    const key = $("vt_api_key").value.trim();
    if(key) fd.append("vt_api_key", key);
    file ? fd.append("eml_file", file) : fd.append("text", text);
    const r = await fetch("/api/check", {method:"POST", body:fd});
    const j = await r.json();
    if(!r.ok) throw new Error(j.error || r.status);
    render(j);
  }catch(e){ alert(T("server") + ": " + e.message); }
  finally{ setLoading(false); }
}
function render(j){
  $("result_area").style.display = "block";
  verdictBadge(j.verdict);
  setText("summary_score", j.total_score ?? j.score);
  setText("summary_confidence", j.confidence);
  setText("summary_source", j.scan_source);
  setText("summary_mode", j.scan_mode || "Standard");
  setText("saved_to", j.saved_to);
  const m = j.meta || {};
  setText("from_meta", m.from);
  setText("reply_meta", m.reply_to);
  setText("subj_meta", m.subject);
  const insights = Array.isArray(j.insights) ? j.insights : (j.insight ? [j.insight] : []);
  $("insights_container").innerHTML = insights.length ? insights.map(insightHtml).join("") : "—";
  const reasons = (j.reasons || []).length ? j.reasons : [T("noReasons")];
  $("reasons").innerHTML = reasons.map(r => `<li>${esc(r)}</li>`).join("");
  window.scrollTo({top: $("result_area").offsetTop - 80, behavior:"smooth"});
}

function initSourceCards(){
  document.querySelectorAll(".source-card").forEach(card => {
    const activate = () => {
      document.querySelectorAll(".source-card").forEach(c => c.classList.remove("active"));
      card.classList.add("active");
      card.querySelector('input[name="scan_source"]').checked = true;
    };
    card.addEventListener("click", activate);
    card.addEventListener("keydown", e => { if(e.key === "Enter" || e.key === " "){ e.preventDefault(); activate(); } });
  });
}
document.addEventListener("DOMContentLoaded", () => { applyLang(lang); initSourceCards(); });
