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
    <title>App CHECKER Pro | Stealth Mode</title>
    <style>
        :root { --neon: #00d4ff; --bg: #050a10; }
        body { background: var(--bg); color: #fff; font-family: sans-serif; text-align: center; padding: 20px; }
        .card { max-width: 450px; margin: auto; background: rgba(10, 25, 41, 0.9); border: 1px solid var(--neon); border-radius: 20px; padding: 25px; box-shadow: 0 0 20px var(--neon); }
        input, select { width: 100%; padding: 12px; margin: 10px 0; border-radius: 10px; background: #000; color: #fff; border: 1px solid #333; box-sizing: border-box; }
        .btn { width: 100%; padding: 15px; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; font-size: 1.1em; transition: 0.3s; margin-top: 10px; }
        .btn-blue { background: var(--neon); color: #000; }
        .btn-green { background: #00ff88; color: #000; }
        .vm-box { width: 100%; height: 350px; margin-top: 20px; display: none; border: 2px solid var(--neon); border-radius: 10px; overflow: hidden; }
        iframe { width: 100%; height: 100%; border: none; }
        #videoResult { display: none; margin-top: 20px; border-top: 1px dashed var(--neon); padding-top: 15px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🛡️ App CHECKER Pro</h2>
        
        <div style="text-align: right; font-size: 0.8em; color: var(--neon);">📊 قسم الإحصائيات</div>
        <input type="text" id="url" placeholder="ضع الرابط المراد فصصه...">
        <button class="btn btn-blue" onclick="fetchStats()">بدء الفحص الرقمي</button>
        <div id="statusText" style="margin: 10px 0; font-size: 0.9em;"></div>

        <hr style="border: 0.5px solid #222; margin: 20px 0;">

        <div style="text-align: right; font-size: 0.8em; color: #00ff88;">🎥 قسم الـ VM والتسجيل</div>
        <select id="duration">
            <option value="10000">تسجيل 10 ثوانٍ</option>
            <option value="30000">تسجيل 30 ثانية</option>
        </select>
        <button class="btn btn-green" id="startBtn">تشغيل البيئة المعزولة 🚀</button>

        <div class="vm-box" id="vmBox">
            <iframe id="ifr"></iframe>
        </div>

        <div id="videoResult">
            <video id="v" width="100%" controls style="border-radius:10px;"></video>
            <a id="dl" style="color:#00ff88; display:block; margin-top:10px; text-decoration:none; font-weight:bold;">⬇️ تحميل تقرير الفيديو</a>
        </div>
    </div>

    <script>
        // 1. الإحصائيات (بدون رسائل مزعجة)
        async function fetchStats() {
            const url = document.getElementById('url').value;
            const status = document.getElementById('statusText');
            if(!url) return;
            status.innerText = "جاري الفحص... ⏳";
            try {
                const r = await fetch('/api/check', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                const d = await r.json();
                status.innerHTML = `⚠️ خبيث: <span style="color:red">${d.malicious}</span> | ✅ سليم: <span style="color:#00ff88">${d.harmless}</span>`;
            } catch(e) { status.innerText = "فشل الاتصال بالخادم."; }
        }

        // 2. التسجيل والـ VM (الطلب المباشر)
        const btn = document.getElementById('startBtn');
        btn.onclick = async () => {
            const url = document.getElementById('url').value;
            const dur = parseInt(document.getElementById('duration').value);
            if(!url) return;

            try {
                // محاولة تشغيل التسجيل رغماً عن القيود
                const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
                const recorder = new MediaRecorder(stream);
                const chunks = [];

                recorder.ondataavailable = e => chunks.push(e.data);
                recorder.onstop = () => {
                    const blob = new Blob(chunks, { type: 'video/webm' });
                    const vidUrl = URL.createObjectURL(blob);
                    document.getElementById('v').src = vidUrl;
                    document.getElementById('dl').href = vidUrl;
                    document.getElementById('dl').download = "checker_scan.webm";
                    document.getElementById('videoResult').style.display = 'block';
                    stream.getTracks().forEach(t => t.stop());
                };

                recorder.start();
                document.getElementById('vmBox').style.display = 'block';
                document.getElementById('ifr').src = url.startsWith('http') ? url : 'https://' + url;
                btn.disabled = true;
                btn.innerText = "🔴 جاري الفحص والتسجيل...";

                setTimeout(() => {
                    recorder.stop();
                    document.getElementById('vmBox').style.display = 'none';
                    btn.disabled = false;
                    btn.innerText = "تشغيل البيئة المعزولة 🚀";
                }, dur);
            } catch(e) {
                // لن نضع alert هنا، إذا فشل سيبقى الزر كما هو
                console.log("الوصول مرفوض");
            }
        };
    </script>
</body>
</html>
'''

@app.route('/')
def index(): return HTML_TEMPLATE

@app.route('/api/check', methods=['POST'])
def check():
    target = request.json.get('url', '')
    url_id = base64.urlsafe_b64encode(target.encode()).decode().strip("=")
    try:
        r = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers={"x-apikey": VT_API_KEY})
        s = r.json()['data']['attributes']['last_analysis_stats']
        return jsonify({"malicious": s['malicious'], "harmless": s['harmless']})
    except: return jsonify({"malicious": "?", "harmless": "?"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
