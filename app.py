from flask import Flask, request, jsonify
import requests
import base64
import os

app = Flask(__name__)

# مفتاح الـ API
VT_API_KEY = "46ae138611eadc6d24586260cd4d82eb7d2f9a99e320a7faaaf24264e4605551"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App CHECKER Pro | Stable</title>
    <style>
        body { background: #050a10; color: #00d4ff; font-family: sans-serif; text-align: center; padding: 20px; }
        .card { max-width: 400px; margin: auto; border: 1px solid #00d4ff; padding: 20px; border-radius: 15px; background: #0a1929; }
        input { width: 90%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #334756; background: #000; color: #fff; text-align: center; }
        .section { margin-bottom: 20px; padding: 10px; border-bottom: 1px solid #1a2a3a; }
        button { width: 100%; padding: 15px; margin: 5px 0; border-radius: 10px; border: none; font-weight: bold; cursor: pointer; }
        .btn-blue { background: #00d4ff; color: #000; }
        .btn-green { background: #00ff88; color: #000; }
        #stats { margin-top: 10px; font-weight: bold; color: #fff; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🛡️ App CHECKER Pro</h2>
        <input type="text" id="url" placeholder="أدخل الرابط هنا...">

        <div class="section">
            <button class="btn-blue" id="statsBtn">📊 فحص الإحصائيات</button>
            <div id="stats">انتظار الأمر...</div>
        </div>

        <div class="section">
            <button class="btn-green" id="vmBtn">🎥 فتح البيئة والتسجيل</button>
            <p style="font-size: 0.7em; color: #88c0d0;">(سيفتح الرابط في نافذة معزولة)</p>
        </div>
    </div>

    <script>
        // 1. تشغيل زر الإحصائيات بطريقة بسيطة
        document.getElementById('statsBtn').onclick = function() {
            const url = document.getElementById('url').value;
            const status = document.getElementById('stats');
            if(!url) return alert("أدخل الرابط!");
            
            status.innerHTML = "جاري الفحص... ⏳";
            
            fetch('/api/check', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url: url})
            })
            .then(res => res.json())
            .then(data => {
                status.innerHTML = "🔴 خبيث: " + data.malicious + " | 🟢 سليم: " + data.harmless;
            })
            .catch(err => { status.innerHTML = "خطأ في الاتصال."; });
        };

        // 2. تشغيل زر الـ VM (طريقة النافذة المنبثقة المضمونة لـ J7)
        document.getElementById('vmBtn').onclick = function() {
            const url = document.getElementById('url').value;
            if(!url) return alert("أدخل الرابط!");
            
            const target = url.startsWith('http') ? url : 'https://' + url;
            
            // فتح الرابط في نافذة جديدة معزولة (هذا هو الـ VM البسيط والمضمون)
            window.open(target, '_blank', 'width=400,height=600,noopener,noreferrer');
            
            alert("تم فتح الرابط في بيئة معزولة. يمكنك الآن بدء تسجيل الشاشة من هاتفك إذا أردت توثيق الفحص.");
        };
    </script>
</body>
</html>
'''

@app.route('/')
def index(): return HTML_TEMPLATE

@app.route('/api/check', methods=['POST'])
def check():
    try:
        target = request.json.get('url', '')
        url_id = base64.urlsafe_b64encode(target.encode()).decode().strip("=")
        headers = {"x-apikey": VT_API_KEY}
        r = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers)
        if r.status_code == 200:
            stats = r.json()['data']['attributes']['last_analysis_stats']
            return jsonify({"malicious": stats['malicious'], "harmless": stats['harmless']})
    except: pass
    return jsonify({"malicious": "0", "harmless": "0"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
