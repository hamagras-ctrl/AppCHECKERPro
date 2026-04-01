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
        body { background: #000; color: #00d4ff; font-family: sans-serif; text-align: center; padding: 20px; }
        .container { max-width: 500px; margin: auto; background: #001f33; padding: 20px; border-radius: 15px; border: 1px solid #00d4ff; }
        input { width: 80%; padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #00d4ff; background: #000; color: #fff; }
        button { padding: 10px 20px; background: #00d4ff; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        #result { margin-top: 20px; padding: 10px; display: none; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>App CHECKER Pro</h1>
        <input type="text" id="urlInput" placeholder="ضع الرابط هنا...">
        <button onclick="checkURL()">فحص الآن</button>
        <div id="result"></div>
    </div>
    <script>
        async function checkURL() {
            const url = document.getElementById('urlInput').value;
            const resDiv = document.getElementById('result');
            resDiv.style.display = "block";
            resDiv.innerHTML = "جاري الفحص...";
            try {
                const response = await fetch('/api/check', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                const data = await response.json();
                resDiv.innerHTML = data.malicious > 0 ? "⚠️ رابط خبيث!" : "✅ رابط آمن.";
            } catch(e) { resDiv.innerHTML = "خطأ في الاتصال."; }
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
    target_url = request.json.get('url')
    url_id = base64.urlsafe_b64encode(target_url.encode()).decode().strip("=")
    headers = {"accept": "application/json", "x-apikey": VT_API_KEY}
    response = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers)
    if response.status_code == 200:
        stats = response.json()['data']['attributes']['last_analysis_stats']
        return jsonify({"malicious": stats['malicious']})
    return jsonify({"malicious": 0})

if __name__ == '__main__':
    app.run()
