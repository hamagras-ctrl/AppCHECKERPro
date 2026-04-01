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
        :root { --primary: #1a73e8; --bg: #0f172a; --card: #1e293b; --text: #f8fafc; }
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; }
        
        /* الهيدر العلوي */
        .header { display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; background: #161e2d; border-bottom: 1px solid #2d3748; }
        .logo-area { display: flex; align-items: center; gap: 10px; }
        .nav-btns { display: flex; gap: 10px; }
        .nav-btn { padding: 8px 15px; border-radius: 8px; border: none; font-size: 0.9em; cursor: pointer; color: #fff; }
        .btn-active { background: var(--primary); }
        .btn-ghost { background: transparent; }

        /* المحتوى الرئيسي */
        .container { max-width: 500px; margin: 40px auto; padding: 20px; text-align: center; }
        .main-icon { width: 80px; height: 80px; background: #1e293b; border-radius: 50%; display: flex; items-center; justify-content: center; margin: 0 auto 20px; border: 4px solid #1a73e822; }
        h1 { font-size: 2.2em; margin-bottom: 10px; font-weight: bold; }
        p.subtitle { color: #94a3b8; margin-bottom: 30px; font-size: 0.95em; }

        /* صندوق الإدخال والأزرار */
        .input-group { background: #334155; border-radius: 15px; display: flex; align-items: center; padding: 5px; margin-bottom: 25px; }
        input { flex: 1; background: transparent; border: none; padding: 15px; color: #fff; text-align: right; font-size: 1em; outline: none; }
        .btn-action { background: var(--primary); color: #fff; border: none; padding: 12px 25px; border-radius: 12px; font-weight: bold; cursor: pointer; }

        /* الأقسام الإضافية */
        .section-card { background: var(--card); border-radius: 15px; padding: 20px; margin-bottom: 20px; border: 1px solid #334155; text-align: right; }
        .section-label { color: var(--primary); font-size: 0.8em; font-weight: bold; margin-bottom: 15px; display: block; border-right: 3px solid var(--primary); padding-right: 10px; }
        
        .btn-secondary { display: block; width: 100%; padding: 12px; border-radius: 10px; text-decoration: none; text-align: center; font-weight: bold; margin-bottom: 10px; }
        .btn-vm { background: #10b981; color: #fff; }
        .btn-rec { border: 1px dashed #ef4444; color: #ef4444; background: #450a0a22; }
        
        #result { font-weight: bold; padding: 10px; color: #38bdf8; }
    </style>
</head>
<body>

    <div class="header">
        <div class="nav-btns">
            <button class="nav-btn btn-ghost">📊 الإحصائيات</button>
            <button class="nav-btn btn-active">الرئيسية</button>
        </div>
        <div class="logo-area">
            <span style="font-weight: bold;">App Checker PRO</span>
            <img src="https://img.icons8.com/color/48/shield.png" width="30">
        </div>
    </div>

    <div class="container">
        <div class="main-icon">
            <img src="https://img.icons8.com/fluency/96/shield.png" width="50">
        </div>
        
        <h1>فحص أمان الروابط</h1>
        <p class="subtitle">تأكد من سلامة أي رابط قبل النقر عليه. نقوم بفحص الروابط ضد قواعد البيانات للبرمجيات الخبيثة.</p>

        <div class="input-group">
            <button class="btn-action" onclick="getStats()">ابدأ الفحص</button>
            <input type="text" id="target" placeholder="أدخل الرابط المراد فصحه...">
        </div>

        <div id="result">في انتظار إدخال الرابط...</div>

        <div class="section-card">
            <span class="section-label">البيئة المعزولة (VM)</span>
            <p style="font-size: 0.85em; color: #94a3b8;">فتح الرابط في نافذة معزولة لتجنب ملفات تعريف الارتباط الخبيثة.</p>
            <a id="vmLink" href="#" target="_blank" class="btn-secondary btn-vm" onclick="prepareVM()">فتح المعاينة الآمنة 🚀</a>
        </div>

        <div class="section-card">
            <span class="section-label">توثيق الفحص</span>
            <div class="btn-secondary btn-rec">
                🔴 ابدأ "مسجل الشاشة" يدوياً لتوثيق الفحص
            </div>
            <p style="font-size: 0.75em; color: #64748b; margin-top: 10px;">بما أنك تستخدم J7، يرجى تفعيل مسجل الشاشة من لوحة التنبيهات قبل فتح المعاينة.</p>
        </div>
    </div>

    <script>
        function getStats() {
            const url = document.getElementById('target').value.trim();
            const res = document.getElementById('result');
            if(!url) return alert("يرجى إدخال الرابط!");
            
            res.innerHTML = "جاري التحليل الرقمي... ⏳";
            fetch('/api/check', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url: url})
            })
            .then(r => r.json())
            .then(data => {
                res.innerHTML = `⚠️ خبيث: ${data.malicious} | ✅ سليم: ${data.harmless}`;
            })
            .catch(() => { res.innerHTML = "فشل الاتصال بخادم الفحص."; });
        }

        function prepareVM() {
            const urlInput = document.getElementById('target').value.trim();
            const link = document.getElementById('vmLink');
            if(!urlInput) return alert("أدخل الرابط أولاً!");
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
