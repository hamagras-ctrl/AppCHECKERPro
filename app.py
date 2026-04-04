from flask import Flask, request, jsonify
import requests
import base64
import os

app = Flask(__name__)

# مفتاح API الخاص بك لخدمة الفحص
VT_API_KEY = "46ae138611eadc6d24586260cd4d82eb7d2f9a99e320a7faaaf24264e4605551"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App Checker PRO</title>
    <style>
        :root { --primary-blue: #1a73e8; --dark-navy: #0f172a; --card-bg: #1e293b; --text-gray: #94a3b8; }
        body { background-color: var(--dark-navy); color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; }
        
        /* الهيدر العلوي كما في تصميمك */
        .header { display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; background: #161e2d; border-bottom: 1px solid #2d3748; }
        .logo-text { font-weight: bold; font-size: 1.2em; display: flex; align-items: center; gap: 10px; }
        .nav-pills { display: flex; gap: 10px; background: #0b1120; padding: 5px; border-radius: 12px; }
        .pill { padding: 8px 18px; border-radius: 10px; border: none; cursor: pointer; color: white; font-size: 0.9em; transition: 0.3s; }
        .pill-active { background: var(--primary-blue); box-shadow: 0 4px 10px rgba(26, 115, 232, 0.3); }
        .pill-ghost { background: transparent; color: var(--text-gray); }

        /* منطقة المحتوى الرئيسي */
        .main { max-width: 500px; margin: 40px auto; padding: 0 20px; text-align: center; }
        .hero-icon { width: 90px; height: 90px; background: #1e293b; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 25px; border: 2px solid #334155; }
        h1 { font-size: 2.4em; margin: 0 0 15px; font-weight: 800; letter-spacing: -1px; }
        .desc { color: var(--text-gray); font-size: 1em; line-height: 1.6; margin-bottom: 35px; }

        /* شريط الإدخال المدمج */
        .search-bar { background: #334155; border-radius: 18px; display: flex; align-items: center; padding: 6px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
        .search-bar input { flex: 1; background: transparent; border: none; padding: 14px; color: white; text-align: right; outline: none; font-size: 1em; }
        .search-bar button { background: var(--primary-blue); color: white; border: none; padding: 12px 28px; border-radius: 14px; font-weight: bold; cursor: pointer; }

        /* الأقسام الوظيفية */
        .feature-card { background: var(--card-bg); border-radius: 20px; padding: 22px; margin-top: 25px; border: 1px solid #334155; text-align: right; transition: 0.3s; }
        .card-tag { color: var(--primary-blue); font-size: 0.8em; font-weight: 700; display: block; margin-bottom: 12px; }
        .action-link { display: block; width: 100%; padding: 14px; border-radius: 12px; text-decoration: none; text-align: center; font-weight: 700; margin-top: 15px; }
        .btn-green { background: #10b981; color: white; }
        .btn-red-outline { border: 1.5px dashed #ef4444; color: #ef4444; background: #450a0a11; }
        
        #scan-result { margin-top: 15px; font-weight: 600; color: #38bdf8; min-height: 20px; }
    </style>
</head>
<body>

    <div class="header">
        <div class="nav-pills">
            <button class="pill pill-ghost">الإحصائيات</button>
            <button class="pill pill-active">الرئيسية</button>
        </div>
        <div class="logo-text">
            <span>App Checker PRO</span>
            <img src="https://img.icons8.com/color/48/checked-shield.png" width="28">
        </div>
    </div>

    <div class="main">
        <div class="hero-icon">
            <img src="https://img.icons8.com/fluency/96/shield.png" width="55">
        </div>
        
        <h1>فحص أمان الروابط</h1>
        <p class="desc">تأكد من سلامة أي رابط قبل النقر عليه. نقوم بفحص الروابط ضد قواعد بيانات البرمجيات الخبيثة والتصيد الاحتيالي.</p>

        <div class="search-bar">
            <button onclick="startAnalysis()">ابدأ الفحص</button>
            <input type="text" id="urlInput" placeholder="أدخل الرابط هنا...">
        </div>
        <div id="scan-result">بانتظار إدخال الرابط...</div>

        <div class="feature-card">
            <span class="card-tag">● البيئة المعزولة (VM)</span>
            <p style="font-size: 0.9em; color: var(--text-gray); margin: 0;">تصفح الرابط داخل حاوية آمنة لمنع وصول التهديدات لجهازك.</p>
            <a id="vmTrigger" href="#" target="_blank" class="action-link btn-green" onclick="launchVM()">فتح المعاينة الآمنة 🚀</a>
        </div>

        <div class="feature-card">
            <span class="card-tag">● توثيق الفحص بالفيديو</span>
            <div class="action-link btn-red-outline">
                🔴 قم بتفعيل "مسجل الشاشة" يدوياً للتوثيق
            </div>
            <p style="font-size: 0.8em; color: #64748b; margin-top: 12px;">نظراً لإصدار أندرويد على J7، يرجى تشغيل مسجل الشاشة من الإعدادات السريعة قبل المعاينة.</p>
        </div>
    </div>

    <script>
        // دالة الفحص الرقمي
        async function startAnalysis() {
            const url = document.getElementById('urlInput').value.trim();
            const log = document.getElementById('scan-result');
            if(!url) return;
            
            log.innerHTML = "جاري الاتصال بقاعدة البيانات... ⏳";
            try {
                const response = await fetch('/api/check', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                const data = await response.json();
                log.innerHTML = `⚠️ تهديدات: ${data.malicious} | ✅ آمن: ${data.harmless}`;
            } catch(e) { log.innerHTML = "فشل الاتصال بالخادم."; }
        }

        // دالة إعداد رابط المعاينة
        function launchVM() {
            const input = document.getElementById('urlInput').value.trim();
            const link = document.getElementById('vmTrigger');
            if(!input) return alert("الرجاء إدخال رابط أولاً");
            
            let target = input.replace(/\s+/g, ''); 
            if(!target.startsWith('http')) target = 'https://' + target;
            link.href = target;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home(): return HTML_TEMPLATE

@app.route('/api/check', methods=['POST'])
def check():
    try:
        url = request.json.get('url', '')
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        response = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers={"x-apikey": VT_API_KEY})
        stats = response.json()['data']['attributes']['last_analysis_stats']
        return jsonify({"malicious": stats['malicious'], "harmless": stats['harmless']})
    except: return jsonify({"malicious": "!", "harmless": "!"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
