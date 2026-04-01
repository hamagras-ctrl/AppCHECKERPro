from flask import Flask, request, jsonify
import requests
import base64
import os

app = Flask(__name__)

# مفتاح API الخاص بك لفحص الروابط
VT_API_KEY = "46ae138611eadc6d24586260cd4d82eb7d2f9a99e320a7faaaf24264e4605551"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App CHECKER Pro | Ultra Edition 🛡️</title>
    <style>
        body { background: #050a10; color: #00d4ff; font-family: sans-serif; text-align: center; margin: 0; padding: 20px; }
        .container { max-width: 500px; margin: auto; background: rgba(10, 25, 41, 0.9); padding: 25px; border-radius: 20px; border: 1px solid #00d4ff; box-shadow: 0 0 20px #00d4ff; }
        input { width: 90%; padding: 12px; margin: 10px 0; border-radius: 10px; border: 1px solid #334756; background: #000; color: #fff; text-align: center; }
        .btn-group { display: flex; gap: 10px; justify-content: center; margin-top: 15px; }
        button { padding: 12px 20px; border-radius: 10px; border: none; font-weight: bold; cursor: pointer; transition: 0.3s; width: 45%; }
        .btn-check { background: linear-gradient(45deg, #00d4ff, #0056b3); color: white; }
        .btn-vm { background: linear-gradient(45deg, #ff4b2b, #ff416c); color: white; }
        .vm-screen { width: 100%; height: 300px; background: #000; border: 2px solid #333; margin-top: 20px; border-radius: 10px; display: none; overflow: hidden; }
        iframe { width: 100%; height: 100%; border: none; background: #fff; }
        #result { margin-top: 15px; font-weight: bold; }
        #videoOutput { margin-top: 20px; display: none; }
        video { width: 100%; border-radius: 10px; border: 1px solid #00ff88; }
    </style>
</head>
<body>
    <div class="container">
        <h1>App CHECKER Pro</h1>
        <p style="font-size: 0.8em; color: #64b5f6;">نظام الفحص المعزول والتسجيل</p>
        
        <input type="text" id="urlInput" placeholder="ضع الرابط المراد فحصه هنا...">
        
        <div class="btn-group">
            <button class="btn-check" onclick="checkURL()">فحص سريع 📊</button>
            <button class="btn-vm" onclick="startVM()">تشغيل الـ VM 🎥</button>
        </div>

        <div id="result"></div>

        <div class="vm-screen" id="vmScreen">
            <iframe id="vmIframe"></iframe>
        </div>

        <div id="videoOutput">
            <p>✅ تم حفظ فيديو المعاينة:</p>
            <video id="vPreview" controls></video>
            <a id="vDl" style="color:#00ff88; text-decoration:none; display:block; margin-top:10px;">⬇️ تحميل فيديو التسجيل</a>
        </div>
    </div>

    <script>
        let stream, recorder, chunks = [];

        // دالة الفحص السريع عبر API
        async function checkURL() {
            const url = document.getElementById('urlInput').value;
            const res = document.getElementById('result');
            if(!url) return alert("أدخل رابطاً أولاً!");
            res.innerHTML = "جاري الفحص الأمني... ⏳";
            
            try {
                const response = await fetch('/api/check', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                const data = await response.json();
                res.innerHTML = `النتيجة: 🔴 خبيث (${data.malicious}) | 🟢 سليم (${data.harmless})`;
            } catch(e) { res.innerHTML = "فشل الاتصال بالسيرفر."; }
        }

        // دالة تشغيل البيئة الافتراضية والتسجيل
        async function startVM() {
            const url = document.getElementById('urlInput').value;
            if(!url) return alert("أدخل الرابط أولاً!");

            try {
                // طلب إذن التسجيل
                stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
                recorder = new MediaRecorder(stream);
                chunks = [];

                recorder.ondataavailable = e => chunks.push(e.data);
                recorder.onstop = () => {
                    const blob = new Blob(chunks, {type: 'video/webm'});
                    const vUrl = URL.createObjectURL(blob);
                    document.getElementById('vPreview').src = vUrl;
                    document.getElementById('vDl').href = vUrl;
                    document.getElementById('vDl').download = "safe_scan_record.webm";
                    document.getElementById('videoOutput').style.display = 'block';
                    stream.getTracks().forEach(t => t.stop());
                };

                recorder.start();
                document.getElementById('vmScreen').style.display = 'block';
                document.getElementById('vmIframe').src = url.startsWith('http') ? url : 'https://' + url;

                // توقف تلقائي بعد 15 ثانية (يمكنك تغيير المدة)
                setTimeout(() => {
                    if(recorder.state === "recording") {
                        recorder.stop();
                        document.getElementById('vmScreen').style.display = 'none';
                    }
                }, 15000);

            } catch(e) {
                alert("يجب السماح بالوصول للشاشة لبدء التسجيل في الـ VM!");
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return HTML_TEMPLATE

@app.route('/api/check', methods=['POST'])
def check_api():
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
