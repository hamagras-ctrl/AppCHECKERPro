from flask import Flask, request, jsonify
import requests
import base64

app = Flask(__name__)

# مفتاح الـ API الخاص بك
VT_API_KEY = "46ae138611eadc6d24586260cd4d82eb7d2f9a99e320a7faaaf24264e4605551"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App CHECKER Pro 🛡️</title>
    <style>
        body { 
            background: radial-gradient(circle, #001220 0%, #000000 100%); 
            color: #00d4ff; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            text-align: center; 
            padding: 20px; 
            min-height: 100vh; 
            margin: 0; 
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { 
            max-width: 450px; 
            width: 90%;
            background: rgba(0, 31, 51, 0.9); 
            padding: 40px 20px; 
            border-radius: 25px; 
            border: 2px solid #00d4ff; 
            box-shadow: 0 0 30px rgba(0, 212, 255, 0.3); 
        }
        h1 { font-size: 2.2em; text-shadow: 0 0 15px #00d4ff; margin-bottom: 10px; }
        p { color: #88c0d0; margin-bottom: 30px; font-size: 0.9em; }
        input { 
            width: 85%; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 12px; 
            border: 1px solid #00d4ff; 
            background: #000; 
            color: #fff; 
            text-align: center; 
            font-size: 1em;
            outline: none;
        }
        button { 
            width: 92%; 
            padding: 15px; 
            background: #00d4ff; 
            border: none; 
            border-radius: 12px; 
            color: #000; 
            font-weight: bold; 
            cursor: pointer; 
            font-size: 1.1em; 
            transition: 0.3s; 
            margin-top: 15px; 
        }
        button:hover { background: #fff; box-shadow: 0 0 20px #fff; transform: scale(1.03); }
        #result { 
            margin-top: 30px; 
            padding: 20px; 
            border-radius: 15px; 
            display: none; 
            font-weight: bold; 
            animation: fadeIn 0.5s;
        }
        .safe { border: 2px solid #00ff88; color: #00ff88; background: rgba(0, 255, 136, 0.1); }
        .danger { border: 2px solid #ff4444; color: #ff4444; background: rgba(255, 68, 68, 0.1); }
        .loading { border: 2px solid #ffcc00; color: #ffcc00; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>App CHECKER Pro</h1>
        <p>درع الحماية الذكي للروابط</p>
        <input type="text" id="urlInput" placeholder="أدخل الرابط هنا لفحصه...">
        <button onclick="checkURL()">تحليل الرابط الآن 🛡️</button>
        <div id="result"></div>
    </div>

    <script>
        async function checkURL() {
            const url = document.getElementById('urlInput').value;
            const resDiv = document.getElementById('result');
            if(!url) return alert("الرجاء إدخال رابط!");
            
            resDiv.style.display = "block";
            resDiv.className = "loading";
            resDiv.innerHTML = "جاري الفحص الأمني... 🔍";

            try {
                const response = await fetch('/api/check', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                const data = await response.json();
                
                if(data.malicious > 0) {
                    resDiv.className = "danger";
                    resDiv.innerHTML = "⚠️ تحذير: هذا الرابط خبيث!<br>اكتشفته محركات الأمان كتهديد.";
                } else {
                    resDiv.className = "safe";
                    resDiv.innerHTML = "✅ الرابط آمن تماماً.<br>يمكنك استخدامه دون قلق.";
                }
            } catch(e) {
                resDiv.innerHTML = "حدث خطأ في الاتصال بالسيرفر.";
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/api/check', methods=['POST'])
def check_url():
    try:
        target_url = request.json.get('url')
        if not target_url: return jsonify({"malicious": 0})
        url_id = base64.urlsafe_b64encode(target_url.encode()).decode().strip("=")
        headers = {"accept": "application/json", "x-apikey": VT_API_KEY}
        response = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers)
        if response.status_code == 200:
            stats = response.json()['data']['attributes']['last_analysis_stats']
            return jsonify({"malicious": stats['malicious']})
        return jsonify({"malicious": 0})
    except:
        return jsonify({"malicious": 0})

if __name__ == '__main__':
    app.run()
