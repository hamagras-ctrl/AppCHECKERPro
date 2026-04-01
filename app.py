from flask import Flask, request, jsonify
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App CHECKER Pro | VM & Recorder</title>
    <style>
        body { background: #050a10; color: #00d4ff; font-family: sans-serif; text-align: center; padding: 20px; }
        .container { max-width: 450px; margin: auto; border: 1px solid #00d4ff; padding: 25px; border-radius: 20px; background: rgba(10, 25, 41, 0.9); box-shadow: 0 0 15px #00d4ff; }
        h1 { text-shadow: 0 0 10px #00d4ff; }
        input, select { width: 95%; padding: 12px; margin: 10px 0; border-radius: 10px; border: 1px solid #334756; background: #000; color: #fff; text-align: center; outline: none; }
        button { background: linear-gradient(45deg, #00d4ff, #0056b3); color: #fff; padding: 15px; border: none; border-radius: 10px; font-weight: bold; width: 100%; cursor: pointer; font-size: 1.1em; transition: 0.3s; }
        button:disabled { background: #555; cursor: not-allowed; }
        .vm-box { width: 100%; height: 350px; margin-top: 20px; display: none; border: 2px solid #00d4ff; border-radius: 10px; overflow: hidden; }
        iframe { width: 100%; height: 100%; border: none; }
        #videoArea { display: none; margin-top: 20px; padding: 15px; background: rgba(0, 255, 136, 0.1); border-radius: 10px; border: 1px solid #00ff88; }
        video { width: 100%; border-radius: 10px; }
        .timer { color: #ff4b2b; font-weight: bold; margin-top: 10px; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ App CHECKER Pro</h1>
        <p style="font-size: 0.9em; color: #88c0d0;">نظام المعاينة المعزولة والتسجيل الذكي</p>
        
        <input type="text" id="url" placeholder="أدخل الرابط المراد فتحه (مثال: google.com)">
        
        <label style="display:block; margin-top:10px; font-size:0.8em;">حدد مدة تسجيل الشاشة:</label>
        <select id="duration">
            <option value="10000">10 ثوانٍ (سريع)</option>
            <option value="30000">30 ثانية (متوسط)</option>
            <option value="60000">دقيقة واحدة (كامل)</option>
            <option value="120000">دقيقتان (مطول)</option>
        </select>

        <button id="startBtn">بدء تشغيل الـ VM والتسجيل 🎥</button>
        
        <div class="timer" id="timerDisplay">متبقي: <span id="seconds">0</span> ثانية</div>

        <div class="vm-box" id="vmBox">
            <iframe id="vmIframe"></iframe>
        </div>

        <div id="videoArea">
            <p style="color:#00ff88;">✅ تم انتهاء المعاينة وحفظ التسجيل:</p>
            <video id="v" controls></video>
            <a id="downloadLink" style="color:#00ff88; display:block; margin-top:10px; text-decoration:none; font-weight:bold;">⬇️ تحميل فيديو التسجيل</a>
        </div>
    </div>

    <script>
        const btn = document.getElementById('startBtn');
        const timerDisplay = document.getElementById('timerDisplay');
        const secondsSpan = document.getElementById('seconds');

        btn.addEventListener('click', async () => {
            const targetUrl = document.getElementById('url').value;
            const duration = parseInt(document.getElementById('duration').value);
            
            if(!targetUrl) return alert("يرجى إدخال الرابط أولاً!");

            try {
                // طلب إذن التسجيل (ستظهر نافذة أندرويد الحقيقية هنا)
                const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
                const recorder = new MediaRecorder(stream);
                const chunks = [];

                recorder.ondataavailable = e => chunks.push(e.data);
                recorder.onstop = () => {
                    const blob = new Blob(chunks, { type: 'video/webm' });
                    const videoUrl = URL.createObjectURL(blob);
                    document.getElementById('v').src = videoUrl;
                    document.getElementById('downloadLink').href = videoUrl;
                    document.getElementById('downloadLink').download = "app_checker_scan.webm";
                    document.getElementById('videoArea').style.display = 'block';
                    timerDisplay.style.display = 'none';
                    stream.getTracks().forEach(t => t.stop());
                };

                // تشغيل الـ VM والبدء
                recorder.start();
                document.getElementById('vmBox').style.display = 'block';
                document.getElementById('vmIframe').src = targetUrl.startsWith('http') ? targetUrl : 'https://' + targetUrl;
                document.getElementById('videoArea').style.display = 'none';

                btn.disabled = true;
                timerDisplay.style.display = 'block';
                
                let timeLeft = duration / 1000;
                secondsSpan.innerText = timeLeft;

                const countdown = setInterval(() => {
                    timeLeft--;
                    secondsSpan.innerText = timeLeft;
                    if(timeLeft <= 0) clearInterval(countdown);
                }, 1000);

                setTimeout(() => {
                    if(recorder.state === "recording") {
                        recorder.stop();
                        document.getElementById('vmBox').style.display = 'none';
                        btn.disabled = false;
                        btn.innerText = "بدء تشغيل الـ VM والتسجيل 🎥";
                    }
                }, duration);

            } catch (err) {
                console.error(err);
                alert("يجب إعطاء الإذن لتسجيل الشاشة لكي يعمل الـ VM!");
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML_TEMPLATE

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
