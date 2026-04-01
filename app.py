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
    <title>App CHECKER Pro | Sandbox</title>
    <style>
        body { background: #000; color: #00d4ff; font-family: sans-serif; text-align: center; padding: 15px; }
        .card { border: 2px solid #00d4ff; padding: 20px; border-radius: 15px; background: #050a10; max-width: 450px; margin: auto; }
        input { width: 90%; padding: 12px; margin: 10px 0; border-radius: 8px; background: #111; color: #fff; border: 1px solid #333; }
        .btn { background: #00d4ff; color: #000; padding: 15px; border: none; border-radius: 10px; font-weight: bold; width: 100%; cursor: pointer; margin-top: 10px; }
        .vm-window { width: 100%; height: 400px; margin-top: 20px; display: none; border: 2px solid #ff4b2b; border-radius: 10px; background: #fff; }
        iframe { width: 100%; height: 100%; border: none; }
        .hint { font-size: 0.8em; color: #88c0d0; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🛡️ App CHECKER Pro</h2>
        <input type="text" id="target" placeholder="ضع الرابط هنا...">
        
        <button class="btn" onclick="runVM()">تشغيل البيئة المعزولة (VM) 🚀</button>
        
        <p class="hint">⚠️ ملاحظة لـ J7: بمجرد فتح البيئة، استخدم "مسجل الشاشة" الخاص بهاتفك لتوثيق العملية.</p>

        <div class="vm-window" id="vmWindow">
            <iframe id="vmIfr"></iframe>
        </div>
    </div>

    <script>
        function runVM() {
            const url = document.getElementById('target').value;
            if(!url) return alert("أدخل رابطاً!");
            
            let cleanUrl = url.trim();
            if(!cleanUrl.startsWith('http')) cleanUrl = 'https://' + cleanUrl;

            // إظهار النافذة وتحميل الرابط
            const win = document.getElementById('vmWindow');
            const ifr = document.getElementById('vmIfr');
            
            win.style.display = 'block';
            ifr.src = cleanUrl;
            
            // تمرير الصفحة للأسفل ليرى المستخدم الـ VM
            window.scrollTo(0, document.body.scrollHeight);
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home(): return HTML_TEMPLATE

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
