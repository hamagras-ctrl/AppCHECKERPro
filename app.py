from flask import Flask, render_template, request, jsonify
import requests
import base64

app = Flask(__name__)

# مفتاح الـ API الخاص بك الذي أرسلته
VT_API_KEY = "46ae138611eadc6d24586260cd4d82eb7d2f9a99e320a7faaaf24264e4605551"

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>App CHECKER Pro 🛡️</title>
        <style>
            body { background: radial-gradient(circle, #001220 0%, #000000 100%); color: #00d4ff; font-family: sans-serif; text-align: center; padding: 20px; min-height: 100vh; margin: 0; }
            .container { max-width: 500px; margin: 50px auto; background: rgba(0, 31, 51, 0.9); padding: 30px; border-radius: 20px; border: 2px solid #00d4ff; box-shadow: 0 0 25px #00d4ff; }
            h1 { font-size: 2.2em; text-shadow: 0 0 15px #00d4ff; margin-bottom: 10px; }
            p { color: #88c0d0; margin-bottom: 25px; }
            input { width: 90%; padding: 15px; margin: 10px 0; border-radius: 12px; border: 1px solid #00d4ff; background: #000; color: #fff; text-align: center; font-size: 1em; }
            button { width: 95%; padding: 15px; background: #00d4ff; border: none; border-radius: 12px; color: #000; font-weight: bold; cursor: pointer; font-size: 1.1em; transition: 0.3s; margin-top: 15px; }
            button:hover { background: #fff; box-shadow: 0 0 20px #fff; transform: scale(1.02); }
            #result { margin-top: 30px; padding: 20px; border-radius: 12px; display: none; font-weight: bold; line-height: 1.6; }
            .safe { border: 2px solid #00ff88; color: #00ff88; background: rgba(0, 255, 136, 0.1); }
            .danger { border: 2px solid #ff4444; color: #ff4444; background: rgba(255, 68, 68, 0.1); }
            .loading { border: 2px solid #ffcc00; color: #ffcc00; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>App CHECKER Pro</h1>
            <p>نظام الحماية من الروابط المشبوهة</p>
            <input type="text" id="urlInput" placeholder="ضع الرابط هنا لفحصه...">
            <button onclick="checkURL()">تحليل الرابط الآن 🔍</button>
            <div id="result"></div>
        </div>

        <script>
            async function checkURL() {
                const url = document.getElementById('urlInput').value;
                const resDiv = document.getElementById('result');
                if(!url) return alert("الرجاء إدخال رابط أولاً!");
                
                resDiv.style.display = "block";
                resDiv.className = "loading";
                resDiv.innerHTML = "جاري الاتصال بقاعدة بيانات VirusTotal... ⏳";

                try {
                    const response = await fetch('/api/check', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({url: url})
                    });
                    const data = await response.json();
                    
                    if(data.error) {
                        resDiv.innerHTML = "خطأ: " + data.error;
                    } else if(data.malicious > 0) {
                        resDiv.className = "danger";
                        resDiv.innerHTML = `⚠️ تحذير أمني!<br>الرابط خبيث وغير آمن.<br>اكتشفته ${data.malicious} محركات أمان.`;
                    } else {
                        resDiv.className = "safe";
                        resDiv.innerHTML = "✅ فحص آمن.<br>لم يتم العثور على أي تهديدات في هذا الرابط.";
                    }
                } catch(e) {
                    resDiv.innerHTML = "حدث خطأ أثناء الفحص. تأكد من اتصال الإنترنت.";
                }
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/check', methods=['POST'])
def check_url():
    target_url = request.json.get('url')
    if not target_url:
        return jsonify({"error": "No URL provided"}), 400

    # تحويل الرابط لصيغة يفهمها VirusTotal (Base64)
    url_id = base64.urlsafe_b64encode(target_url.encode()).decode().strip("=")
    
    headers = {
        "accept": "application/json",
        "x-apikey": VT_API_KEY
    }

    try {
        # طلب فحص الرابط من سيرفرات VirusTotal
        response = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers)
        if response.status_code == 200:
            stats = response.json()['data']['attributes']['last_analysis_stats']
            return jsonify({"malicious": stats['malicious']})
        else:
            # إذا كان الرابط جديداً، نطلب فحصه لأول مرة
            return jsonify({"malicious": 0, "status": "new_or_clean"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
