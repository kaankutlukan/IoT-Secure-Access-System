import RPi.GPIO as GPIO
import time
import hashlib
import os
import firebase_admin
from firebase_admin import credentials, db
from pirc522 import RFID
import telebot 
from datetime import datetime
import threading 

GPIO.setwarnings(False)
try:
    GPIO.cleanup() 
except:
    pass

FIREBASE_CRED_PATH = 'serviceAccountKey.json'
FIREBASE_DB_URL = 'https://<YOUR-PROJECT-ID>.firebasedatabase.app'
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID'

BUTTON_PIN = 17 
HASH_SALT = "bu_cok_gizli_bir_salt_degeridir_12345"


print("Sistem başlatılıyor...")


try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CRED_PATH)
        firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_DB_URL})
    ref = db.reference('cards')
    print("Firebase bağlantısı başarılı.")
except Exception as e:
    print(f"HATA: Firebase başlatılamadı! -> {e}")
    exit()

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
rc522 = RFID(pin_mode=GPIO.BCM, pin_irq=None)


last_scanned_data = None


def log_to_web(mesaj):
    """Hem terminale yazar hem siteye gönderir."""
    print(mesaj)
    try:
        zaman = datetime.now().strftime("%H:%M:%S")
        db.reference('system_logs').push({
            'text': mesaj,
            'time': zaman
        })
    except:
        pass

def generate_permanent_password():
    return os.urandom(8).hex()

def generate_dynamic_hash(uid):
    data_to_hash = f"{uid}-{time.time()}-{HASH_SALT}".encode('utf-8')
    hash_object = hashlib.sha256(data_to_hash)
    return hash_object.hexdigest()

def telegram_worker():
    global last_scanned_data
    
    if last_scanned_data:
        try:
            uid = last_scanned_data['uid']
            password = last_scanned_data.get('password', '-')
            dynamic_hash = last_scanned_data.get('hash', '-')
            scan_time = last_scanned_data.get('last_scanned_at', 'Bilinmiyor')
            
            message = (
                f"--- YENİ KART BİLGİSİ GÖNDERİLDİ ---\n"
                f"Kart UID: {uid}\n"
                f"Zaman: {scan_time}\n"
                f"Kalıcı Şifre: {password}\n"
                f"Dinamik Hash: {dynamic_hash}"
            )
            
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
            log_to_web("Telegram'a mesaj başarıyla gönderildi.")
            
        except Exception as e:
            log_to_web(f"HATA: Telegram'a mesaj gönderilemedi! -> {e}")
    else:
        log_to_web("Telegram'a gönderilecek veri bulunamadı. (Önce kart okutun)")
        try:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Gönderilecek kart verisi yok. Lütfen önce kart okutun.")
        except:
            pass

def trigger_telegram_background():
    log_to_web(f"\nButona basıldı. Telegram'a gönderim deneniyor...")
    threading.Thread(target=telegram_worker).start()

try:
    log_to_web("-" * 30)
    log_to_web("SİSTEM ÇALIŞMAYA HAZIR.")
    log_to_web("Kart okutmak için bekleniyor...")
    
    while True:
        (error, data) = rc522.request()
        if not error:
            (error, uid) = rc522.anticoll()
            if not error:
                uid_str = "".join([str(i) for i in uid])
                log_to_web(f"\nKart okundu! UID: {uid_str}")
                
                try:
                    card_ref = ref.child(uid_str)
                    card_data = card_ref.get()
                    new_hash = generate_dynamic_hash(uid_str)
                    
                    readable_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    status_msg = ""
                    
                    if card_data is None:
                        status_msg = "Yeni Kayıt"
                        log_to_web(f"Yeni kart algılandı. Kalıcı şifre oluşturuluyor...")
                        new_password = generate_permanent_password()
                        
                        data_to_save = { 
                            'uid': uid_str, 
                            'password': new_password, 
                            'hash': new_hash, 
                            'created_at': readable_date,
                            'last_scanned_at': readable_date,
                            'status': 'active'
                        }
                        card_ref.set(data_to_save)
                        log_to_web("Yeni kart Firebase'e başarıyla kaydedildi.")
                        
                    else:
                                       status_msg = "Tanıdık Personel"
                        log_to_web(f"Tanıdık kart algılandı. Hash güncelleniyor...")
                        new_password = card_data['password']
                        
                        data_to_save = { 
                            'uid': uid_str, 
                            'password': new_password, 
                            'hash': new_hash, 
                            'last_scanned_at': readable_date
                        }
                        card_ref.update(data_to_save)
                        log_to_web("Kartın hash bilgisi Firebase'de güncellendi.")
                    
                                   last_scanned_data = {
                        'uid': uid_str,
                        'password': new_password,
                        'hash': new_hash,
                        'last_scanned_at': readable_date,
                        'status': status_msg
                    }
                    
                    log_to_web("-" * 20)
                    
                except Exception as e:
                    log_to_web(f"HATA: Firebase işlemi sırasında bir hata oluştu: {e}")
                
                time.sleep(1) 

        if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
            trigger_telegram_background()
            time.sleep(0.5) 

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nProgram sonlandırılıyor.")
finally:
    GPIO.cleanup()
    print("Pinler temizlendi.")
