from flask import Flask, render_with_template, request, send_from_directory
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import requests
import time

app = Flask(__name__)

# إنشاء مجلد لحفظ لقطات الشاشة
SCREENSHOT_FOLDER = 'static/screenshots'
if not os.path.exists(SCREENSHOT_FOLDER):
    os.makedirs(SCREENSHOT_FOLDER)

# دالة لتحليل أمان الموقع
def check_security(url):
    report = {}
    
    # 1. التحقق من بروتوكول HTTPS
    if url.startswith("https://"):
        report['protocol'] = {'text': 'يستخدم HTTPS (مشفر)', 'safe': True}
    elif url.startswith("http://"):
        report['protocol'] = {'text': 'يستخدم HTTP (غير مشفر، خطر!)', 'safe': False}
    else:
        report['protocol'] = {'text': 'بروتوكول غير معروف أو تنسيق رابط خاطئ', 'safe': None}

    # 2. التحقق من شهادة SSL
    try:
        if url.startswith("http"):
            response = requests.get(url, timeout=5)
            # إذا لم يحدث خطأ في الطلب، فالشهادة صالحة
            if response.url.startswith("https://"):
                report['ssl'] = {'text': 'شهادة SSL صالحة ومفعلة', 'safe': True}
            else:
                report['ssl'] = {'text': 'الموقع لا يستخدم شهادة SSL', 'safe': False}
    except requests.exceptions.SSLError:
        report['ssl'] = {'text': 'خطأ في شهادة SSL أو الشهادة منتهية، خطر!', 'safe': False}
    except requests.exceptions.RequestException as e:
        report['ssl'] = {'text': f'فشل في الاتصال للتحقق: {str(e)}', 'safe': None}
    
    # تحديد مستوى الأمان الإجمالي
    if all(r['safe'] for r in report.values() if r['safe'] is not None):
        report['overall'] = 'الموقع يبدو آمناً'
        report['level'] = '🟢'
    else:
        report['overall'] = 'الموقع قد يمثل خطراً!'
        report['level'] = '🔴'
        
    return report

# دالة لفتح الموقع وأخذ لقطة شاشة
def capture_screenshot(url):
    # إعدادات متصفح كروم للعمل في الخلفية
    chrome_options = Options()
    chrome_options.add_argument("--headless") # لا يفتح نافذة المتصفح الحقيقية
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # تعيين حجم النافذة لأخذ لقطة كاملة
    chrome_options.add_argument("--window-size=1280,1024")
    
    # تشغيل متصفح كروم
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        # انتظر قليلاً لتحميل الصفحة
        time.sleep(3) 
        
        # إنشاء اسم فريد للملف
        filename = f"screenshot_{int(time.time())}.png"
        filepath = os.path.join(SCREENSHOT_FOLDER, filename)
        
        # أخذ لقطة الشاشة وحفظها
        driver.save_screenshot(filepath)
        
        driver.quit()
        return filename
    except Exception as e:
        driver.quit()
        return None

# دالة لعرض الصفحة الرئيسية والتعامل مع طلبات التحقق
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # استقبال الرابط من النموذج
        target_url = request.form.get('url')
        
        # إضافة بروتوكول إذا لم يكن موجوداً
        if not target_url.startswith("http"):
            target_url = "http://" + target_url
            
        # 1. أخذ لقطة شاشة
        screenshot_file = capture_screenshot(target_url)
        
        # 2. تحليل أمان الموقع
        security_report = check_security(target_url)
        
        # عرض النتيجة في نفس الصفحة
        return render_with_template('index.html', 
                               url=target_url, 
                               screenshot=screenshot_file, 
                               report=security_report)

    # عرض الصفحة الرئيسية
    return render_with_template('index.html', url=None, screenshot=None, report=None)

# مسار للوصول إلى لقطات الشاشة
@app.route('/screenshots/<filename>')
def get_screenshot(filename):
    return send_from_directory(SCREENSHOT_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)