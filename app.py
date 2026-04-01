from flask import Flask, os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App CHECKER Pro</title>
    <style>
        body { background: #000; color: #00d4ff; font-family: sans-serif; text-align: center; padding: 20px; }
        .box { border: 2px solid #00d4ff; padding: 20px; border-radius: 15px; background: #0a1929; }
        button { background: #00d4ff; color: #000; padding: 15px; border: none; border-radius: 10px; font-weight: bold; width: 100%; font-size: 1.1em; cursor: pointer; }
        #vm { width: 100%; height: 300px; display: none; margin-top: 20px; border: 1px solid #555; }
    </style>
</head>
<body>
    <div class="box">
        <h1>🛡️ App CHECKER Pro</h1>
        <input type="text" id="url" placeholder="أدخل الرابط..." style="width:90%; padding:10px; margin-bottom:10px; border-radius:5px;">
        <br>
        <label>مدة التسجيل:</label>
        <select id="time" style="padding:10px; margin-bottom:10px;">
            <option value="10000">10 ثوانٍ</option>
            <option value="30000">30 ثانية</option>
        </select>
        <button id="go">بدء تشغيل الـ VM والتسجيل 🎥</button>
        <div id="vm"><iframe id="ifr" style="width:100%; height:100%; border:none;"></iframe></div>
        <div id="res" style="display:none; margin-top:20px;">
            <video id="vid" width="100%" controls></video>
        </div>
    </div>

    <script>
        document.getElementById('go').onclick = async function() {
            const url = document.getElementById('url').value;
            const dur = document.getElementById('time').value;
            if(!url) return alert("ضع رابطاً!");

            try {
                // طلب الإذن الحقيقي (ستظهر نافذة أندرويد هنا)
                const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
                const recorder = new MediaRecorder(stream);
                const chunks = [];

                recorder.ondataavailable = e => chunks.push(e.data);
                recorder.onstop = () => {
                    const blob = new Blob(chunks, { type: 'video/webm' });
                    document.getElementById('vid').src = URL.createObjectURL(blob);
                    document.getElementById('res').style.display = 'block';
                    stream.getTracks().forEach(t => t.stop());
                };

                recorder.start();
                document.getElementById('vm').style.display = 'block';
                document.getElementById('ifr').src = url.startsWith('http') ? url : 'https://' + url;

                setTimeout(() => {
                    if(recorder.state === "recording") {
                        recorder.stop();
                        document.getElementById('vm').style.display = 'none';
                    }
                }, dur);
            } catch (err) {
                // إذا رفض المستخدم أو لم يدعم المتصفح
                console.log(err);
            }
        };
    </script>
</body>
</html>
'''

@app.route('/')
def home(): return HTML_TEMPLATE

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
