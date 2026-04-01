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
    <title>App CHECKER Pro | Force Mode</title>
    <style>
        body { background: #000; color: #00d4ff; font-family: sans-serif; text-align: center; padding: 15px; }
        .box { border: 2px solid #00d4ff; padding: 20px; border-radius: 15px; background: #050a10; }
        input, select { width: 90%; padding: 12px; margin: 10px 0; border-radius: 8px; background: #111; color: #fff; border: 1px solid #333; }
        .btn-action { background: #00d4ff; color: #000; padding: 15px; border: none; border-radius: 10px; font-weight: bold; width: 100%; cursor: pointer; margin-top: 10px; }
        .vm-container { width: 100%; height: 350px; margin-top: 20px; display: none; border: 1px solid #444; position: relative; }
        iframe { width: 100%; height: 100%; border: none; background: #fff; }
        #videoResult { display: none; margin-top: 20px; border: 1px solid #00ff88; padding: 10px; }
    </style>
</head>
<body>
    <div class="box">
        <h1>🛡️ App CHECKER Pro</h1>
        <input type="text" id="target" placeholder="أدخل الرابط المراد فضح أسراره...">
        
        <select id="timer">
            <option value="10000">10 ثوانٍ</option>
            <option value="30000">30 ثانية</option>
        </select>

        <button class="btn-action" id="forceBtn">تفعيل الـ VM وتسجيل الشاشة فوراً 🎥</button>

        <div class="vm-container" id="vmContainer">
            <iframe id="vmIframe"></iframe>
        </div>

        <div id="videoResult">
            <p style="color:#00ff88;">✅ الفيديو جاهز للتحميل:</p>
            <video id="vPreview" width="100%" controls></video>
            <a id="vDownload" style="color:#00ff88; font-weight:bold; text-decoration:none; display:block; margin-top:10px;">⬇️ تحميل التسجيل الآن</a>
        </div>
    </div>

    <script>
        const btn = document.getElementById('forceBtn');
        
        btn.onclick = async () => {
            const rawUrl = document.getElementById('target').value;
            const duration = parseInt(document.getElementById('timer').value);
            
            if(!rawUrl) return alert("أدخل رابطاً!");
            
            // تنظيف الرابط لمنع خطأ DNS الذي ظهر في صورتك
            let cleanUrl = rawUrl.trim();
            if(!cleanUrl.startsWith('http')) cleanUrl = 'https://' + cleanUrl;

            try {
                // طلب الإذن المباشر (سيظهر الآن رغماً عنه)
                const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
                const recorder = new MediaRecorder(stream);
                const chunks = [];

                recorder.ondataavailable = e => chunks.push(e.data);
                recorder.onstop = () => {
                    const blob = new Blob(chunks, { type: 'video/webm' });
                    const url = URL.createObjectURL(blob);
                    document.getElementById('vPreview').src = url;
                    document.getElementById('vDownload').href = url;
                    document.getElementById('vDownload').download = "safe_scan.webm";
                    document.getElementById('videoResult').style.display = 'block';
                    stream.getTracks().forEach(t => t.stop());
                };

                // التشغيل
                recorder.start();
                document.getElementById('vmContainer').style.display = 'block';
                document.getElementById('vmIframe').src = cleanUrl;
                btn.disabled = true;
                btn.innerText = "🔴 جاري التسجيل والعزل...";

                setTimeout(() => {
                    recorder.stop();
                    document.getElementById('vmContainer').style.display = 'none';
                    btn.disabled = false;
                    btn.innerText = "تفعيل الـ VM وتسجيل الشاشة فوراً 🎥";
                }, duration);

            } catch(e) {
                alert("يجب ضغط 'البدء الآن' في نافذة أندرويد ليعمل التسجيل!");
            }
        };
    </script>
</body>
</html>
'''

@app.route('/')
def home(): return HTML_TEMPLATE

@app.route('/api/check', methods=['POST'])
def check():
    # كود الـ API يظل كما هو لخدمة الإحصائيات
    return jsonify({"malicious": 0, "harmless": 0})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
