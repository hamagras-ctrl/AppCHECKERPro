from flask import Flask, request, jsonify
import requests
import base64
import os

app = Flask(__name__)

VT_API_KEY = "46ae138611eadc6d24586260cd4d82eb7d2f9a99e320a7faaaf24264e4605551"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App Checker PRO</title>
    <style>
        :root { --primary: #1a73e8; --bg: #0f172a; --card: #1e293b; }
        body { background: var(--bg); color: white; font-family: sans-serif; margin: 0; padding: 0; overflow-x: hidden; }
        
        .header { display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; background: #161e2d; border-bottom: 1px solid #2d3748; }
        .nav-pills { display: flex; gap: 8px; }
        .pill { padding: 6px 15px; border-radius: 8px; border: none; color: white; cursor: pointer; font-size: 0.85em; }
        .pill-active { background: var(--primary); }
        .pill-ghost { background: transparent; color: #94a3b8; }

        .container { max-width: 480px; margin: 20px auto; padding: 0 15px; text-align: center; }
        h1 { font-size: 1.8em; margin-bottom: 5px; }
        .subtitle { color: #94a3b8; font-size: 0.9em; margin-bottom: 20px; }

        .search-box { background: #334155; border-radius: 15px; display: flex; padding: 5px; margin-bottom: 20px; }
        input { flex: 1; background: transparent; border: none; padding: 12px; color: white; text-align: right; outline: none; }
        .btn-scan { background: var(--primary); color: white; border: none; padding: 10px 20px; border-radius: 12px; font-weight: bold; }

        .section { background: var(--card); border-radius: 15px; padding: 15px; margin-bottom: 15px; border: 1px solid #334155; text-align: right; }
        .tag { color: var(--primary); font-size: 0.75em; font-weight: bold; margin-bottom: 10px; display: block; }
        
        /* قسم العرض الداخلي (المتصفح الخاص بالتطبيق) */
        .internal-browser { width: 100%; height: 400px; background: #fff; border-radius: 12px; display: none; margin-top: 15px; overflow: hidden; border: 2px solid var(--primary); }
        iframe { width: 100%; height: 100%; border: none; }

        .btn-view { display: block; width: 100%; padding: 12px; background: #10b981; color: white; text-decoration: none; text-align: center; border-radius: 10px; font-weight: bold; border: none; cursor: pointer; }
        #res { margin: 10px 0; font-weight: bold; color: #38bdf8; font-size: 0.9em; }
    </style>
</head>
<body>

    <div class="header">
        <div class="nav-pills">
            <button class="pill pill-ghost">الإحصائيات</button>
            <button class="pill pill-active">الرئيسية</button>
        </div>
        <div style="font-weight: bold; font-size: 1em;">App Checker PRO</div>
    </div>

    <div class="container">
        <h1>فحص أمان الروابط</h1>
        <p class="subtitle">تأكد من سلامة الروابط داخل تطبيقك الخاص.</p>

        <div class="search-box">
            <button class="btn-scan" onclick="runScan()">ابدأ الفحص</button>
            <input type="text" id="urlIn" placeholder="ضع الرابط هنا...">
        </div>
        <div id="res">بانتظار الرابط...</div>

        <div class="section">
            <span class="tag">● عرض الفحص المباشر</span>
            <button class="btn-view" onclick="showInside()">فتح المعاينة داخل التطبيق 🚀</button>
            
            <div class="internal-browser" id="browserWindow">
                <iframe id="targetFrame"></iframe>
            </div>
        </div>

        <div class="section" style="border: 1px dashed #ef4444;">
            <span class="tag" style="color:#ef4444;">● توثيق الفيديو</span>
            <p style="font-size: 0.8em; color: #94a3b8; margin: 0;">شغل مسجل الشاشة الآن لتصوير ما يحدث في الإطار أعلاه.</p>
        </div>
    </div>

    <script>
        function runScan() {
            const url = document.getElementById('urlIn').value.trim();
            if(!url) return;
            document.getElementById('res').innerText = "جاري التحليل... ⏳";
            fetch('/api/check', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url: url})
            }).then(r => r.json()).then(d => {
                document.getElementById('res').innerHTML = `⚠️ خبيث: ${d.malicious} | ✅ آمن: ${d.harmless}`;
            });
        }

        function showInside() {
            const url = document.getElementById('urlIn').value.trim();
            if(!url) return alert("أدخل رابطاً!");
            
            let final = url.replace(/\s+/g, ''); 
            if(!final.startsWith('http')) final = 'https://' + final;

            // إظهار النافذة داخل التطبيق وتحميل الموقع
            document.getElementById('browserWindow').style.display = 'block';
            document.getElementById('targetFrame').src = final;
            
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
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
        r = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers={"x-apikey": VT_API_KEY})
        s = r.json()['data']['attributes']['last_analysis_stats']
        return jsonify({"malicious": s['malicious'], "harmless": s['harmless']})
    except: return jsonify({"malicious": "!", "harmless": "!"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
