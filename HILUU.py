import os
import re
import webbrowser
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# --- Ultra Modern Dark Dashboard Interface ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Website Detection & Live Auditor</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 40px; display: flex; justify-content: center; }
        .wrapper { width: 100%; max-width: 850px; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
        h1 { font-size: 26px; text-align: center; color: #38bdf8; margin-bottom: 5px; }
        p.subtitle { text-align: center; color: #94a3b8; margin-top: 0; margin-bottom: 25px; }
        .input-group { display: flex; gap: 10px; margin-bottom: 25px; }
        input[type="text"] { flex: 1; padding: 14px; background: #334155; border: 1px solid #475569; border-radius: 6px; color: white; font-size: 16px; outline: none; }
        input[type="text"]:focus { border-color: #38bdf8; }
        button { background: #0284c7; color: white; border: none; padding: 14px 28px; font-size: 16px; font-weight: bold; border-radius: 6px; cursor: pointer; transition: 0.2s; }
        button:hover { background: #0369a1; }
        .badge { display: inline-block; padding: 10px 20px; border-radius: 6px; font-weight: bold; font-size: 18px; margin-bottom: 20px; text-align: center; width: 95%; }
        .safe { background: #166534; color: #bbf7d0; }
        .suspicious { background: #854d0e; color: #fef08a; }
        .danger { background: #991b1b; color: #fecaca; }
        .report-section { background: #334155; border-radius: 8px; padding: 20px; margin-top: 20px; }
        h3 { margin-top: 0; border-bottom: 1px solid #475569; padding-bottom: 8px; color: #38bdf8; }
        .tech-box { background: #1e293b; border-left: 4px solid #38bdf8; padding: 12px 15px; margin-bottom: 15px; border-radius: 0 6px 6px 0; }
        .tech-title { font-weight: bold; color: #94a3b8; font-size: 14px; }
        .tech-value { margin: 5px 0 0 0; color: #f8fafc; font-size: 18px; font-weight: bold; }
        .details-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 10px; }
        .details-item { background: #1e293b; padding: 12px; border-radius: 6px; font-size: 14px; color: #cbd5e1; border: 1px solid #475569; }
        .details-item strong { color: #38bdf8; display: block; margin-bottom: 4px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
        ul { padding-left: 20px; margin: 0; }
        li { margin-bottom: 10px; line-height: 1.5; color: #cbd5e1; }
        .cricket-card { background: #1e293b; border-radius: 6px; padding: 12px; margin-bottom: 8px; border-left: 4px solid #22c55e; }
    </style>
</head>
<body>
    <div class="wrapper">
        <h1>🔍 Website Detection & Live Auditor</h1>
        <p class="subtitle">Extracts topic category, matches/schedule, full technical components & security logs</p>

        <form method="POST">
            <div class="input-group">
                <input type="text" name="url" placeholder="Enter target URL (e.g., cricbuzz.com, espncricinfo.com)" required value="{{ url }}">
                <button type="submit">Scan Website</button>
            </div>
        </form>

        {% if verdict %}
            <div class="badge {{ badge_class }}">
                Security Status: {{ verdict }}
            </div>

            <div class="report-section">
                <h3>1. Website Topic / Purpose</h3>
                <div class="tech-box">
                    <div class="tech-title">This website content is based on:</div>
                    <div class="tech-value">{{ website_category }}</div>
                </div>
            </div>

            {% if is_cricket_site %}
            <div class="report-section" style="border: 1px solid #22c55e;">
                <h3 style="color: #22c55e;">🏏 Live Cricket Status & Matches Hub (Extracted Info)</h3>
                <p style="color: #94a3b8; font-size: 14px; margin-top: -5px; margin-bottom: 15px;">Website ke andar se dhoondhi gayi live matches aur timing ki list:</p>

                {% if cricket_data %}
                    {% for match in cricket_data %}
                        <div class="cricket-card">
                            <p style="margin: 0; font-size: 15px; color: #f8fafc; font-weight: bold;">{{ match }}</p>
                        </div>
                    {% endfor %}
                {% else %}
                    <p style="color: #fda4af;">⚠️ Page par abhi koi active match text ya schedules direct pakad mein nahi aaye (Ho sakta hai content JavaScript se load ho raha ho).</p>
                {% endif %}
            </div>
            {% endif %}

            <div class="report-section">
                <h3>2. Website Metadata (Identity)</h3>
                <div class="details-grid">
                    <div class="details-item" style="grid-column: span 2;"><strong>Meta Title</strong> {{ site_details.title }}</div>
                    <div class="details-item" style="grid-column: span 2;"><strong>Meta Description</strong> {{ site_details.description }}</div>
                    <div class="details-item"><strong>Hosting Server / CDN</strong> {{ site_details.server }}</div>
                    <div class="details-item"><strong>Content Language</strong> {{ site_details.lang }}</div>
                </div>
            </div>

            <div class="report-section">
                <h3>3. Website Inside Components (What is in it?)</h3>
                <div class="details-grid">
                    <div class="details-item"><strong>Total Hyperlinks (&lt;a&gt;)</strong> {{ site_details.total_links }} links found on page</div>
                    <div class="details-item"><strong>Total Images (&lt;img&gt;)</strong> {{ site_details.total_images }} images loaded</div>
                    <div class="details-item"><strong>Headings Count (H1 - H3)</strong> {{ site_details.total_headings }} structure blocks</div>
                    <div class="details-item"><strong>Interactive Forms (&lt;form&gt;)</strong> {{ site_details.total_forms }} forms detected</div>
                    <div class="details-item"><strong>Total Input Fields (&lt;input&gt;)</strong> {{ site_details.total_inputs }} input box / fields</div>
                    <div class="details-item"><strong>Total Action Buttons (&lt;button&gt;)</strong> {{ site_details.total_buttons }} clickable buttons</div>
                    <div class="details-item"><strong>JavaScript Files (&lt;script&gt;)</strong> {{ site_details.total_scripts }} scripts running</div>
                    <div class="details-item"><strong>Style Sheets (&lt;link rel="stylesheet"&gt;)</strong> {{ site_details.total_styles }} CSS files</div>
                </div>
            </div>

            <div class="report-section">
                <h3>4. Built With (Tech Stack / Frameworks)</h3>
                <div class="tech-box" style="border-left-color: #a855f7;">
                    <div class="tech-title">Detected Technologies:</div>
                    <div class="tech-value" style="font-size: 16px; color: #e2e8f0;">{{ detected_tech }}</div>
                </div>
            </div>

            <div class="report-section">
                <h3>5. Security & Vulnerability Audit Logs</h3>
                <ul>
                    {% for finding in findings %}
                        <li>{{ finding }}</li>
                    {% endfor %}
                </ul>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""


def detect_website_category(soup, html_content):
    text_content = html_content.lower()
    title_text = soup.title.string.lower() if soup.title else ""
    meta_desc = soup.find("meta", attrs={"name": "description"})
    desc_text = meta_desc.get("content", "").lower() if meta_desc else ""

    categories = {
        "🏏 Cricket / Sports Portal": ["cricket", "cricbuzz", "ipl", "t20", "scorecard", "match", "stadium", "player",
                                      "football", "sports", "score"],
        "🛒 E-Commerce / Online Shopping Store": ["shop", "store", "buy", "cart", "checkout", "amazon", "flipkart",
                                                 "product", "price", "discount"],
        "📰 News, Blog & Media Platform": ["news", "breaking", "article", "journal", "politics", "daily", "newspaper"],
        "🏦 Finance, Banking & Crypto Exchange": ["bank", "finance", "loan", "insurance", "crypto", "bitcoin",
                                                 "investment", "trading"],
        "🎮 Gaming, Esports & Downloads": ["game", "gaming", "play", "esports", "pubg", "xbox", "steam"]
    }

    category_scores = {}
    for category, keywords in categories.items():
        score = 0
        for kw in keywords:
            if kw in title_text: score += 5
            if kw in desc_text: score += 3
            if kw in text_content: score += 1
        if score > 0:
            category_scores[category] = score

    if category_scores:
        return max(category_scores, key=category_scores.get)
    return "🌐 General Corporate / Portfolio / Multi-purpose Web Application"


def extract_cricket_info(soup):
    """Website ke HTML content se matches, scores aur schedules nikalne ka logic"""
    matches = []

    # 1. Cricket sites ke specific anchors, classes aur structures ko dhoondhna
    # Hum headings, paragraphs aur anchor links ko scan karenge jisme cricket terms honge
    potential_blocks = soup.find_all(['a', 'div', 'p', 'h3', 'h2'])

    seen = set()
    for block in potential_blocks:
        text = block.get_text().strip()
        text_clean = " ".join(text.split())  # Extra spaces remove karne ke liye

        # Match information patterns ko filter karne ke liye rules
        if len(text_clean) > 15 and len(text_clean) < 120:
            # Agar text mein 'vs', 'won by', 'opt to', 'tomorrow', 'pm ist' ya live scores jaise patterns hain
            if any(k in text_clean.lower() for k in
                   [" vs ", " won by ", " match ", " live ", " opt to ", " am ist ", " pm ist ", "tomorrow",
                    "yesterday", "runs", "wickets"]):
                if text_clean not in seen:
                    # Filter out purely generic navigation items
                    if not any(ignore in text_clean.lower() for ignore in
                               ["click here", "privacy policy", "terms of use", "download app"]):
                        matches.append(text_clean)
                        seen.add(text_clean)

    return matches[:8]  # Top 8 important updates/matches return karenge taaki UI bheege nahi


def detect_technology(html_content, headers, soup):
    tech_stack = []
    html_lower = html_content.lower()
    server = headers.get("Server", "").lower()
    powered_by = headers.get("X-Powered-By", "").lower()

    if "cloudflare" in server: tech_stack.append("Cloudflare (CDN/Security)")
    if "nginx" in server:
        tech_stack.append("Nginx (Web Server)")
    elif "apache" in server:
        tech_stack.append("Apache (Web Server)")
    if "wp-content" in html_lower or "wp-includes" in html_lower: tech_stack.append("WordPress (CMS)")
    if "shopify" in html_lower: tech_stack.append("Shopify (E-commerce Engine)")
    if "laravel" in powered_by or "laravel_session" in html_lower: tech_stack.append("Laravel (PHP)")
    if "react" in html_lower or "_next/" in html_lower: tech_stack.append("React.js / Next.js Framework")
    if "jquery" in html_lower: tech_stack.append("jQuery (JS Library)")
    if "bootstrap" in html_lower: tech_stack.append("Bootstrap (CSS UI)")
    if "tailwind" in html_lower: tech_stack.append("Tailwind (Utility CSS)")

    if not tech_stack:
        return "Custom HTML5 / Vanilla JavaScript"
    return ", ".join(list(set(tech_stack)))


def scan_live_html(url):
    findings = []
    danger_score = 0
    website_category = "Unknown"
    detected_tech = "Unknown"
    cricket_data = []
    is_cricket_site = False

    site_details = {
        "title": "Not Found", "description": "Not Found", "server": "Hidden / Protected", "lang": "Unknown",
        "total_links": 0, "total_images": 0, "total_headings": 0, "total_forms": 0,
        "total_inputs": 0, "total_buttons": 0, "total_scripts": 0, "total_styles": 0
    }

    target_url = url.strip()
    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(target_url, headers=headers, timeout=7)
        html_content = response.text
        findings.append(f"🟢 Successfully connected to server. HTTP Status Code: {response.status_code}")

        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Detect Category
        website_category = detect_website_category(soup, html_content)
        detected_tech = detect_technology(html_content, response.headers, soup)

        # 2. Cricket Site specific logic check
        if "Cricket" in website_category:
            is_cricket_site = True
            cricket_data = extract_cricket_info(soup)

        # 3. Extract Identity Metadata
        if soup.title and soup.title.string:
            site_details["title"] = soup.title.string.strip()
        meta_d = soup.find("meta", attrs={"name": "description"}) or soup.find("meta",
                                                                               attrs={"property": "og:description"})
        if meta_d and meta_d.get("content"):
            site_details["description"] = meta_d.get("content").strip()
        site_details["server"] = response.headers.get("Server", "Hidden / Cloudflare")
        html_tag = soup.find("html")
        if html_tag and html_tag.get("lang"):
            site_details["lang"] = html_tag.get("lang").upper()

        # 4. Extract Inside Components Count
        site_details["total_links"] = len(soup.find_all("a"))
        site_details["total_images"] = len(soup.find_all("img"))
        site_details["total_headings"] = len(soup.find_all(["h1", "h2", "h3"]))
        site_details["total_forms"] = len(soup.find_all("form"))
        site_details["total_inputs"] = len(soup.find_all("input"))
        site_details["total_buttons"] = len(soup.find_all("button"))
        site_details["total_scripts"] = len(soup.find_all("script"))
        site_details["total_styles"] = len(soup.find_all("link", attrs={"rel": "stylesheet"}))

    except requests.exceptions.RequestException as e:
        return "Scanner Error", "danger", [f"🔴 Error: {str(e)}"], "None", site_details, "None", [], False

    # --- Security Logic ---
    if response.url.startswith("http://"):
        danger_score += 2
        findings.append("🔴 CRITICAL: Connection is unencrypted (HTTP).")
    else:
        findings.append("🟢 Connection uses encrypted SSL/TLS (HTTPS).")

    for idx, form in enumerate(soup.find_all("form"), 1):
        action = form.get("action", "").lower()
        has_password = any(inp.get("type", "").lower() == "password" for inp in form.find_all("input"))
        if has_password:
            findings.append(f"⚠️ Form #{idx} collects passwords.")
            if action.startswith("http://") or (action and not action.startswith("/") and "http" in action):
                danger_score += 3
                findings.append(f"🔴 EXPLOIT: Form #{idx} sends data to insecure link.")

    if danger_score >= 3.5:
        return "Malicious / High Threat", "danger", findings, website_category, site_details, detected_tech, cricket_data, is_cricket_site
    elif danger_score >= 1:
        return "Suspicious Profile", "suspicious", findings, website_category, site_details, detected_tech, cricket_data, is_cricket_site
    else:
        return "Clean / Safe Web Page", "safe", findings, website_category, site_details, detected_tech, cricket_data, is_cricket_site


@app.route("/", methods=["GET", "POST"])
def home():
    url = ""
    verdict = None
    badge_class = None
    findings = []
    website_category = ""
    detected_tech = ""
    site_details = {}
    cricket_data = []
    is_cricket_site = False

    if request.method == "POST":
        url = request.form["url"]
        verdict, badge_class, findings, website_category, site_details, detected_tech, cricket_data, is_cricket_site = scan_live_html(
            url)

    return render_template_string(
        HTML_TEMPLATE,
        url=url, verdict=verdict, badge_class=badge_class,
        findings=findings, website_category=website_category,
        site_details=site_details, detected_tech=detected_tech,
        cricket_data=cricket_data, is_cricket_site=is_cricket_site
    )


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        webbrowser.open("http://127.0.0.1:5000/")
    app.run(debug=True)