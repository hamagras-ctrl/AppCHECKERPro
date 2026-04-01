from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def main():
    return '''
    <body style="background:#000; color:#00d4ff; text-align:center; padding-top:50px; font-family:sans-serif;">
        <h1>🛡️ App CHECKER Pro</h1>
        <p>الموقع يعمل الآن بنجاح!</p>
        <button style="padding:10px 20px; background:#00d4ff; border:none; border-radius:5px;" 
        onclick="alert('سيتم تفعيل الـ VM الآن')">ابدأ الفحص</button>
    </body>
    '''

if __name__ == "__main__":
    # هذا السطر مهم جداً لفتح الموقع في Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
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
    <title>App CHECKER Pro | Ultra 🛡️</title>
    <style>
        body { background: #050a10; color: #00d4ff; font-family: sans-serif; text-align: center; margin: 0; padding: 20px; }
        .container { max-width: 500px; margin: auto; background: rgba(10, 25, 41, 0.9); padding: 25px; border-radius: 20px; border: 1px solid #00d4ff; box-shadow: 0 0 20px #00d4ff; }
        input, select { width: 90%; padding: 12px; margin: 10px 0; border-radius: 10px; border: 1px solid #334756; background: #000; color: #fff; text-align: center; }
        .btn-group { display: flex; gap: 10px; justify-content: center; }
        button { padding: 12px 20px; border-radius: 10px; border: none; font-weight: bold; cursor: pointer; transition: 0.3s; }
        .btn-check { background: linear-gradient(45deg, #00d4ff, #0056b3); color: white; }
        .btn-vm { background: linear-gradient(45deg, #ff4b2b, #ff416c); color: white; }
        .vm-screen { width: 100%; height: 300px; background: #000; border: 2px solid #333; margin-top: 15px; border-radius: 10px; display: none; overflow: hidden; }
        iframe { width: 100%; height: 100%; border: none; background: #fff; }
        #result { margin-top: 15px; font-size: 0.9em; }
        .stat-box { background: rgba(0,0,0,0.4); padding: 10px; border-radius: 8px; border: 1px solid #334756; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>App CHECKER Pro</h1>
        <input type="text" id="urlInput" placeholder="أدخل الرابط للفحص...">
        
        <select id="duration">
            <option value="10000">تسجيل 10 ثوانٍ</option>
            <option value="30000">تسجيل 30 ثانية</option>
        </select>

        <div class="btn-group">
            <button class="btn-check" onclick="checkURL()">فحص إحصائيات 📊</button>
            <button class="btn-vm" onclick="startVM()">تشغيل VM وتسجيل 🎥</button>
        </div>

        <div id="result"></div>

        <div class="vm-screen" id="vmScreen">
            <iframe id="vmIframe"></iframe>
        </div>

        <div id="videoOutput" style="margin-top:15px; display:none;">
            <video id="vPreview" width="100%" controls></video>
            <a id="vDl" style="color:#00ff88; display:block; margin-top:5px;">⬇️ تحميل التسجيل</a>
        </div>
    </div>

    <script>
        let stream, recorder, chunks = [];

        async function checkURL() {
            const url = document.getElementById('urlInput').value;
            const res = document.getElementById('result');
            if(!url) return alert("أدخل رابطاً!");
            res.innerHTML = "جاري الفحص... ⏳";
            try {
                const response = await fetch('/api/check', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                const data = await response.json();
                res.innerHTML = `<div class="stat-box">🔴 خبيث: ${data.malicious} | 🟢 سليم: ${data.harmless}</div>`;
            } catch(e) { res.innerHTML = "خطأ في الاتصال."; }
        }

        async function startVM() {
            const url = document.getElementById('urlInput').value;
            const dur = document.getElementById('duration').value;
            if(!url) return alert("أدخل رابطاً!");

            try {
                stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
                recorder = new MediaRecorder(stream);
                chunks = [];
                recorder.ondataavailable = e => chunks.push(e.data);
                recorder.onstop = () => {
                    const blob = new Blob(chunks, {type: 'video/webm'});
                    const vUrl = URL.createObjectURL(blob);
                    document.getElementById('vPreview').src = vUrl;
                    document.getElementById('vDl').href = vUrl;
                    document.getElementById('vDl').download = "safe_scan.webm";
                    document.getElementById('videoOutput').style.display = 'block';
                    stream.getTracks().forEach(t => t.stop());
                };

                recorder.start();
                document.getElementById('vmScreen').style.display = 'block';
                document.getElementById('vmIframe').src = url.startsWith('http') ? url : 'https://' + url;

                setTimeout(() => {
                    if(recorder.state === "recording") recorder.stop();
                    document.getElementById('vmScreen').style.display = 'none';
                }, dur);
            } catch(e) { alert("يجب السماح بتسجيل الشاشة!"); }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return HTML_TEMPLATE

@app.route('/api/check', methods=['POST'])
def check_url():
    target = request.json.get('url')
    url_id = base64.urlsafe_b64encode(target.encode()).decode().strip("=")
    headers = {"x-apikey": VT_API_KEY}
    r = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers)
    if r.status_code == 200:
        stats = r.json()['data']['attributes']['last_analysis_stats']
        return jsonify({"malicious": stats['malicious'], "harmless": stats['harmless']})
    return jsonify({"malicious": 0, "harmless": 0})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
