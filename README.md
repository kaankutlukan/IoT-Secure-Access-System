IoT Secure Access System & SOC Dashboard

Bu proje, fiziksel güvenlik ile siber güvenliği bir araya getiren, IoT tabanlı uçtan uca (End-to-End) bir geçiş kontrol sistemidir. Sistem, Raspberry Pi üzerinde çalışarak donanımsal RFID okumalarını gerçekleştirir, verileri şifreler ve gerçek zamanlı olarak bir web arayüzü (SOC Paneli) ile senkronize eder. 

Aynı zamanda Remote Command Execution mantığıyla web üzerinden fiziksel donanıma komut gönderilmesini ve Telegram API üzerinden anlık uyarıların iletilmesini sağlar.

Proje Özellikleri

 Dinamik Hash Şifreleme (SHA-256): Okutulan kartların UID bilgileri zaman damgası ve benzersiz bir "Salt" değeri ile hash'lenerek Firebase'e kaydedilir. Veritabanı sızsa bile kart bilgileri koruma altındadır.
 Gerçek Zamanlı Veritabanı (Firebase RTDB): Tüm kart okumaları ve sistem logları milisaniyeler içinde web arayüzüne yansır.
 Telegram Entegrasyonu: Yetkisiz veya dikkat çeken girişlerde Telegram botu üzerinden yöneticiye anında uyarı mesajı iletilir.
 Web Tabanlı SOC Paneli: Güvenlik operasyon merkezi mantığıyla tasarlanmış arayüz üzerinden canlı loglar izlenebilir, sisteme uzaktan "Başlat/Durdur" komutları gönderilebilir ve eski kart kayıtları silinebilir.

Kullanılan Teknolojiler

Donanım: Raspberry Pi, RC522 RFID Okuyucu Modülü
Backend (Arka Plan): Python 3, hashlib, threading
Frontend (Arayüz): HTML5, CSS3, JavaScript (Firebase SDK)
Veritabanı & Haberleşme: Firebase Realtime Database, Telegram Bot API

 Kurulum ve Çalışma Mantığı

1. `rfid_telegram.py` betiği arka planda sürekli olarak RFID modülünü dinler.
2. `bekci.py` (Watchdog) scripti, sistemin sürekliliğini ve otonom çalışmasını sağlar.
3. Web panelinden gönderilen komutlar Firebase üzerinden dinlenerek donanım üzerinde aksiyona dönüştürülür.
4. Sistemin çalışması için ilgili API anahtarlarının kendi Firebase ve Telegram hesaplarınıza göre düzenlenmesi gerekmektedir.
