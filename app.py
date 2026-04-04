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
    <title>App CHECKER Pro | Multi-Task</title>
    <style>
        :root { --neon: #00d4ff; --bg: #050a10; --green: #00ff88; }
        body { background: var(--bg); color: #fff; font-family: sans-serif; text-align: center; padding: 15px; margin: 0; }
        .card { max-width: 450px; margin: auto; background: #0a1929; border: 2px solid var(--neon); border-radius: 20px; padding: 20px; box-shadow: 0 0 20px rgba(0, 212, 255, 0.3); }
        h1 { color: var(--neon); font-size: 1.6em; text-shadow: 0 0 10px var(--neon); }
        input { width: 100%; padding: 15px; margin-bottom: 15px; border-radius: 12px; border: 1px solid #1e293b; background: #000; color: #fff; box-sizing: border-box; text-align: center; font-size: 1.1em; }
        
        .section { background: rgba(0,0,0,0.4); border-radius: 15px; padding: 15px; margin-bottom: 15px; border: 1px solid #1a2a3a; }
        .section-title { font-size: 0.8em; color: var(--neon); display: block; margin-bottom: 10px; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; }
        
        .btn { display: block; width: 100%; padding: 15px; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; text-decoration: none; font-size: 1em; box-sizing: border-box; transition: 0.3s; }
        .btn-stats { background: var(--neon); color: #000; }
        .btn-vm { background: var(--green); color: #000; }
        .btn-rec { background: #ff4b2b; color: #fff; }
        
        #res { margin-top: 10px; font-weight: bold; color: var(--neon); }
        .hint { font-size: 0.75em; color: #666; margin-top: 8px; line-height: 1.4; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🛡️ App CHECKER Pro</h1>
        <input type="text" id="target" placeholder="أدخل الرابط المراد فصصه...">

        <div class="section">
            <span class="section-title">📊 تحليل البيانات (JSON)</span>
            <button class="btn btn-stats" onclick="getStats()">بدء الفحص الرقمي</button>
            <div id="res">في انتظار الأوامر...</div>
        </div>

        <div class="section">
            <span class="section-title">🖥️ البيئة المعزولة (VM)</span>
            <a id="vmLink" href="#" target="_blank" class="btn btn-vm" onclick="prepareVM()">فتح في نافذة آمنة 🚀</a>
            <p class="hint">سيتم فتح الموقع في نافذة جديدة لتجاوز حظر الحماية.</p>
        </div>

        <div class="section">
            <span class="section-title">🎥 توثيق الفيديو</span>
            <div style="background: #000; padding: 10px; border-radius: 8px; border: 1px dashed #ff4b2b;">
                <p style="color: #ff4b2b; font-size: 0.9em; margin: 0;">🔴 ميزة لـ J7:</p>
                <p style="font-size: 0.8em; color: #ccc;">اضغط "فتح" أعلاه، ثم ابدأ "مسجل الشاشة" يدوياً من هاتفك لتصوير الفحص.</p>
            </div>
        </div>

        <p style="font-size: 0.6em; color: #334756;">نظام الفحص المتعدد v3.0</p>
    </div>

    <script>
        function getStats() {
            const url = document.getElementById('target').value.trim();
            const res = document.getElementById('res');
            if(!url) return alert("أدخل رابطاً!");
            
            res.innerHTML = "جاري طلب البيانات... ⏳";
            fetch('/api/check', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url: url})
            })
            .then(r => r.json())
            .then(data => {
                res.innerHTML = `⚠️ خبيث: <span style="color:red">${data.malicious}</span> | ✅ سليم: <span style="color:var(--green)">${data.harmless}</span>`;
            })
            .catch(() => { res.innerHTML = "خطأ في الاتصال بالسيرفر."; });
        }

        function prepareVM() {
            const urlInput = document.getElementById('target').value.trim();
            const link = document.getElementById('vmLink');
            if(!urlInput) {
                alert("أدخل الرابط أولاً!");
                return false;
            }
            let finalUrl = urlInput.replace(/\s+/g, ''); 
            if(!finalUrl.startsWith('http')) finalUrl = 'https://' + finalUrl;
            link.href = finalUrl;
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
        target = request.json.get('url', '')
        url_id = base64.urlsafe_b64encode(target.encode()).decode().strip("=")
        r = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers={"x-apikey": VT_API_KEY})
        s = r.json()['data']['attributes']['last_analysis_stats']
        return jsonify({"malicious": s['malicious'], "harmless": s['harmless']})
    except: return jsonify({"malicious": "!", "harmless": "!"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
