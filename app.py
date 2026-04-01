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
