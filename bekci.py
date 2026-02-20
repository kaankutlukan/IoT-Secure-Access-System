import time
import subprocess
import os
import sys  
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

FIREBASE_KEY_PATH = "serviceAccountKey.json"
DATABASE_URL = "https://<YOUR-PROJECT-ID>.firebasedatabase.app/"
PROJE_DOSYASI = "rfid_telegram.py" # Tetiklenecek ana sistem dosyasinin adi

PYTHON_YOLU = sys.executable 

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_KEY_PATH)
    firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})

print(f"🛡️ BEKÇİ HAZIR: {PYTHON_YOLU} kullanılıyor.")
print("Emir bekleniyor...")

son_islem = "yok"

def log_yaz(mesaj):
    zaman = datetime.now().strftime("%H:%M:%S")
    try:
        db.reference('system_logs').push({'time': zaman, 'text': mesaj})
        print(f"📝 Log: {mesaj}")
    except:
        pass

try:
    while True:
        try:
            emir = db.reference('system_status').get()
        except:
            time.sleep(2)
            continue

        if emir == "start":
            if son_islem != "start":
                print("🟢 BAŞLAT EMRİ GELDİ! (Venv ile başlatılıyor...)")
                
                
                os.system("pkill -f rfid_telegram.py")
                time.sleep(1)
                
                if os.path.exists(PROJE_DOSYASI):
                    subprocess.Popen([PYTHON_YOLU, PROJE_DOSYASI])
                    log_yaz("✅ SİSTEM BAŞLATILDI")
                    son_islem = "start"
                else:
                    print(f"❌ HATA: Dosya bulunamadı! {PROJE_DOSYASI}")
                    son_islem = "hata"

        elif emir == "stop":
            if son_islem != "stop":
                print("🔴 DURDUR EMRİ GELDİ!")
                os.system("pkill -f rfid_telegram.py")
                log_yaz("⛔ SİSTEM KAPATILDI")
                son_islem = "stop"

        time.sleep(2)

except KeyboardInterrupt:
    print("Bekçi kapatıldı.")
