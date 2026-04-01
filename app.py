from flask import Flask, request, jsonify
import requests
import base64

app = Flask(__name__)

VT_API_KEY = "46ae138611eadc6d24586260cd4d82eb7d2f9a99e320a7faaaf24264e4605551"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App CHECKER Pro | Recorder 🎥</title>
    <style>
        body { background: #02050a; color: #00d4ff; font-family: sans-serif; padding: 20px; text-align: center; }
        .container { max-width: 500px; margin: auto; background: rgba(0, 20, 40, 0.9); padding: 20px; border-radius: 15px; border: 2px solid #00d4ff; }
        .vm-screen { width: 100%; height: 300px; background: #000; border: 3px solid #333; margin-top: 15px; display: none; }
        iframe { width: 100%; height: 100%; border: none; background: #fff; }
        input { width: 80%; padding: 12px; margin: 10px 0; background: #000; border: 1px solid #00d4ff; color: #fff; }
        .btn-rec { background: #ff4444; color: white; padding: 12px; width: 45%; border-radius: 8px; border:none; font-weight:bold; }
        .btn-run { background: #00ff88; color: black; padding: 12px; width: 45%; border-radius: 8px; border:none; font-weight:bold; display:none; }
        #status { font-size: 0.8em; color: #ffcc00; margin: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>App CHECKER Pro</h2>
        <p id="status">الخطوة 1: اضغط على زر التسجيل للأذن</p>
        
        <input type="text" id="targetUrl" placeholder="ضع الرابط هنا...">
        
        <div style="display:flex; gap:10px; justify-content:center;">
            <button id="authBtn" class="btn-rec" onclick="getPermission()">1. إذن التسجيل 🎥</button>
            <button id="runBtn" class="btn-run" onclick="startVM()">2. تشغيل الـ VM 🚀</button>
        </div>

        <div class="vm-screen" id="vmContainer">
            <iframe id="vmIframe"></iframe>
        </div>
        
        <div id="videoContainer" style="margin-top:20px; display:none;">
            <video id="finalVideo" width="100%" controls></video>
            <a id="dl" style="color:#00ff88; display:block; margin-top:10px;">⬇️ حفظ التسجيل</a>
        </div>
    </div>

    <script>
        let recorder;
        let stream;
        let chunks = [];

        async function getPermission() {
            try {
                // محاولة طلب الإذن بشكل منفصل وبسيط جداً ليتناسب مع J7
                stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
                document.getElementById('authBtn').style.display = 'none';
                document.getElementById('runBtn').style.display = 'inline-block';
                document.getElementById('status').innerHTML = "✅ تم أخذ الإذن! الآن اضغط تشغيل الـ VM.";
            } catch (e) {
                alert("لم يتم إعطاء الإذن. تأكد من تحديث صفحة الموقع.");
            }
        }

        async function startVM() {
            const url = document.getElementById('targetUrl').value;
            if(!url) return alert("أدخل الرابط!");

            recorder = new MediaRecorder(stream);
            chunks = [];
            recorder.ondataavailable = e => chunks.push(e.data);
            recorder.onstop = () => {
                const blob = new Blob(chunks, {type: 'video/webm'});
                const vUrl = URL.createObjectURL(blob);
                document.getElementById('finalVideo').src = vUrl;
                document.getElementById('dl').href = vUrl;
                document.getElementById('dl').download = "record.webm";
                document.getElementById('videoContainer').style.display = 'block';
            };

            recorder.start();
            document.getElementById('vmContainer').style.display = 'block';
            document.getElementById('vmIframe').src = url.startsWith('http') ? url : 'https://' + url;
            document.getElementById('status').innerHTML = "🔴 جاري التسجيل داخل الـ VM... (سيتوقف بعد 10 ثوانٍ)";

            setTimeout(() => {
                recorder.stop();
                stream.getTracks().forEach(t => t.stop());
                document.getElementById('vmContainer').style.display = 'none';
                document.getElementById('status').innerHTML = "✅ انتهى التسجيل. انظر للأسفل.";
            }, 10000);
        }
    </script>
</body>
</html>
'''
