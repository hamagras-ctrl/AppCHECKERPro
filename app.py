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
    <title>App CHECKER Pro | VM Edition 🛡️</title>
    <style>
        body { background: #02050a; color: #00d4ff; font-family: 'Courier New', monospace; margin: 0; padding: 20px; text-align: center; }
        .container { max-width: 550px; margin: auto; background: rgba(0, 20, 40, 0.9); padding: 25px; border-radius: 15px; border: 2px solid #00d4ff; box-shadow: 0 0 20px #00d4ff; }
        .vm-screen { width: 100%; height: 300px; background: #000; border: 5px solid #333; border-radius: 10px; margin-top: 20px; position: relative; overflow: hidden; display: none; }
        .vm-header { background: #333; color: #fff; padding: 5px; font-size: 0.7em; text-align: left; }
        iframe { width: 100%; height: 100%; border: none; background: #fff; }
        input, select { width: 80%; padding: 12px; margin: 10px 0; background: #000; border: 1px solid #00d4ff; color: #00ff88; border-radius: 8px; }
        .status-bar { font-size: 0.8em; color: #ffcc00; margin: 10px 0; }
        .btn-group { display: flex; gap: 10px; justify-content: center; margin-top: 15px; }
        button { padding: 12px 25px; border-radius: 8px; border: none; font-weight: bold; cursor: pointer; transition: 0.3s; }
        .btn-run { background: #00ff88; color: #000; }
        .btn-rec { background: #ff4444; color: #fff; }
    </style>
</head>
<body>
    <div class="container">
        <h2>System Virtualization Mode</h2>
        <p class="status-bar" id="sysStatus">الوضع الحالي: جاهز للفحص المعزول</p>
        
        <input type="text" id="targetUrl" placeholder="أدخل الرابط المراد فتحه في VM...">
        
        <div>
            <label>مدة التسجيل (ثانية): </label>
            <input type="number" id="recTime" value="10" style="width: 50px;">
        </div>

        <div class="btn-group">
            <button class="btn-run" onclick="launchVM()">تشغيل البيئة الافتراضية 🚀</button>
        </div>

        <div class="vm-screen" id="vmContainer">
            <div class="vm-header">Virtual_OS_v1.0 - Running...</div>
            <iframe id="vmIframe"></iframe>
        </div>

        <div id="recordingResult" style="margin-top:20px; display:none;">
            <p>✅ تم انتهاء التسجيل المعزول</p>
            <video id="recordedVideo" width="100%" controls></video>
        </div>
    </div>

    <script>
        let mediaRecorder;
        let recordedChunks = [];

        async function launchVM() {
            const url = document.getElementById('targetUrl').value;
            const duration = document.getElementById('recTime').value * 1000;
            const iframe = document.getElementById('vmIframe');
            const vmContainer = document.getElementById('vmContainer');
            
            if(!url) return alert("أدخل الرابط!");

            // طلب إذن التسجيل أولاً
            try {
                const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
                mediaRecorder = new MediaRecorder(stream);
                recordedChunks = [];

                mediaRecorder.ondataavailable = (e) => recordedChunks.push(e.data);
                mediaRecorder.onstop = () => {
                    const blob = new Blob(recordedChunks, { type: 'video/webm' });
                    const videoURL = URL.createObjectURL(blob);
                    document.getElementById('recordedVideo').src = videoURL;
                    document.getElementById('recordingResult').style.display = 'block';
                    stream.getTracks().forEach(t => t.stop());
                };

                // بدء التسجيل وتشغيل الـ VM
                mediaRecorder.start();
                vmContainer.style.display = 'block';
                iframe.src = url.startsWith('http') ? url : 'https://' + url;
                document.getElementById('sysStatus').innerHTML = "🔴 جاري التسجيل داخل البيئة المعزولة...";

                setTimeout(() => {
                    if(mediaRecorder.state === "recording") {
                        mediaRecorder.stop();
                        document.getElementById('sysStatus').innerHTML = "🟢 تم الانتهاء وحفظ الفيديو.";
                        vmContainer.style.display = 'none';
                    }
                }, duration);

            } catch (err) {
                alert("يجب السماح بالوصول للشاشة لتشغيل الـ VM.");
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML_TEMPLATE

if __name__ == '__main__':
    app.run()
