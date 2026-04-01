from flask import Flask, request, jsonify
import requests
import base64
import os

app = Flask(__name__)

# مفتاح الـ API للفحص
VT_API_KEY = "46ae138611eadc6d24586260cd4d82eb7d2f9a99e320a7faaaf24264e4605551"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App CHECKER Pro | Organized</title>
    <style>
        :root { --neon-blue: #00d4ff; --neon-green: #00ff88; --bg-dark: #050a10; }
        body { background: var(--bg-dark); color: #fff; font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 15px; }
        .main-card { max-width: 500px; margin: auto; background: rgba(10, 25, 41, 0.95); border-radius: 20px; border: 1px solid var(--neon-blue); padding: 20px; box-shadow: 0 0 20px rgba(0, 212, 255, 0.2); }
        h2 { color: var(--neon-blue); text-align: center; margin-bottom: 20px; }
        
        /* تصنيف الأقسام */
        .section-box { background: rgba(0,0,0,0.3); border: 1px solid #334756; border-radius: 12px; padding: 15px; margin-bottom: 20px; }
        .section-title { font-size: 0.9em; color: var(--neon-blue); margin-bottom: 10px; display: block; border-right: 3px solid var(--neon-blue); padding-right: 10px; }
        
        input, select { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #334756; background: #000; color: #fff; box-sizing: border-box; }
        
        .btn { width: 100%; padding: 12px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.3s; margin-top: 5px; }
        .btn-stats { background: var(--neon-blue); color: #000; }
        .btn-vm { background: var(--neon-green); color: #000; }
        
        #statsResult { margin-top: 10px; font-size: 0.85em; text-align: center; }
        .vm-display { width: 100%; height: 300px; background: #000; margin-top: 15px; display: none; border: 2px solid #444; border-radius: 8px; overflow: hidden; }
        iframe { width: 100%; height: 100%; border: none; }
        #videoArea { display: none; margin-top: 15px; padding: 10px; background: rgba(0,255,136,0.1); border-radius: 8px; border: 1px solid var(--neon-green); }
    </style>
</head>
<body>
    <div class="main-card">
        <h2>🛡️ App CHECKER Pro</h2>
        
        <input type="text" id="targetUrl" placeholder="أدخل الرابط (مثال: google.com)">

        <div class="section-box">
            <span class="section-title">📊 قسم الإحصائيات السريعة</span>
            <button class="btn btn-stats" onclick="fetchStats()">بدء الفحص الرقمي</button>
            <div id="statsResult">جاهز للفحص...</div>
        </div>

        <div class="section-box">
            <span class="section-title">🎥 قسم المعاينة والـ VM</span>
            <label style="font-size: 0.7em;">مدة التسجيل:</label>
            <select id="recDuration">
                <option value="10000">10 ثوانٍ</option>
                <option value="30000">30 ثانية</option>
                <option value="60000">دقيقة كاملة</option>
            </select>
            <button class="btn btn-vm" id="vmBtn">فتح البيئة الافتراضية والتسجيل</button>
            
            <div class="vm-display" id="vmScreen">
                <iframe id="vmIfr"></iframe>
            </div>
        </div>

        <div id="videoArea">
            <p style="font-size:0.8em; color:var(--neon-green);">✅ اكتمل التسجيل بنجاح:</p>
            <video id="vPreview" width="100%" controls></video>
            <a id="vDownload" style="color:var(--neon-green); text-decoration:none; display:block; text-align:center; margin-top:10px;">⬇️ تحميل الفيديو</a>
        </div>
    </div>

    <script>
        // دالة الإحصائيات
        async function fetchStats() {
            const url = document.getElementById('targetUrl').value;
            const resDiv = document.getElementById('statsResult');
            if(!url) return alert("ضع الرابط أولاً!");
            resDiv.innerHTML = "جاري الاتصال بقاعدة البيانات... ⏳";
            try {
                const response = await fetch('/api/check', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                const data = await response.json();
                resDiv.innerHTML = `⚠️ خبيث: <span style="color:red">${data.malicious}</span> | ✅ سليم: <span style="color:#00ff88">${data.harmless}</span>`;
            } catch(e) { resDiv.innerHTML = "تعذر الحصول على إحصائيات."; }
        }

        // دالة الـ VM والتسجيل
        const vmBtn = document.getElementById('vmBtn');
        vmBtn.onclick = async () => {
            const url = document.getElementById('targetUrl').value;
            const dur = parseInt(document.getElementById('recDuration').value);
            if(!url) return alert("ضع الرابط أولاً!");

            try {
                const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
                const recorder = new MediaRecorder(stream);
                const chunks = [];

                recorder.ondataavailable = e => chunks.push(e.data);
                recorder.onstop = () => {
                    const blob = new Blob(chunks, { type: 'video/webm' });
                    const vUrl = URL.createObjectURL(blob);
                    document.getElementById('vPreview').src = vUrl;
                    document.getElementById('vDownload').href = vUrl;
                    document.getElementById('vDownload').download = "scan_report.webm";
                    document.getElementById('videoArea').style.display = 'block';
                    stream.getTracks().forEach(t => t.stop());
                };

                recorder.start();
                document.getElementById('vmScreen').style.display = 'block';
                document.getElementById('vmIfr').src = url.startsWith('http') ? url : 'https://' + url;
                vmBtn.disabled = true;
                vmBtn.innerText = "جاري التسجيل الآن...";

                setTimeout(() => {
                    recorder.stop();
                    document.getElementById('vmScreen').style.display = 'none';
                    vmBtn.disabled = false;
                    vmBtn.innerText = "فتح البيئة الافتراضية والتسجيل";
                }, dur);
            } catch(e) { console.log(e); }
        };
    </script>
</body>
</html>
'''

@app.route('/')
def home(): return HTML_TEMPLATE

@app.route('/api/check', methods=['POST'])
def check_api():
    target = request.json.get('url', '')
    url_id = base64.urlsafe_b64encode(target.encode()).decode().strip("=")
    headers = {"x-apikey": VT_API_KEY}
    r = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers)
    if r.status_code == 200:
        stats = r.json()['data']['attributes']['last_analysis_stats']
        return jsonify({"malicious": stats['malicious'], "harmless": stats['harmless']})
    return jsonify({"malicious": "غير متوفر", "harmless": "غير متوفر"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
