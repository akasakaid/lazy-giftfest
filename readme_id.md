# Lazy-GiftFest

Auto play/Auto merge game @giftfest telegram bot

## Fitur

* Auto merge / Play game
* Daily check in
* Mengecek daily task
* Klaim reward / join undian di main quest

## Cara menggunakan

Pastikan komputermu sudah terinstall python dan git.

```
git clone https://github.com/akasakaid/lazy-giftfest.git
cd lazy-giftfest
python -m pip install -r requirements.txt
```

Buat file `data.txt` dan `proxies.txt`

Ambil data query akun kamu dan paste/isikan ke file `data.txt`. Perbaris berisi 1 data akun.

Contoh isi file `data.txt`

```
query_id=123......
query_id=456......
query_id=789......
```

Jika kamu ingin menggunakan proxy, kamu bisa mengisi file `proxies.txt`, format yang digunakan :

Jika menggunakan autentikasi:

```
http://user:password@ip_proxy:port
```

Jika tidak menggunakan autentikasi:

```
http://ip_proxy:port
```

Setelah semua itu, eksekusi file main.py 

```
python main.py
```

## Cara mendapatkan query data akun

1. Kamu harus mengaktifkan opsi devtool diaplikasi telegram desktop. Kamu bisa menonton video ini [https://www.youtube.com/watch?v=NYxHmck_GjE&pp=0gcJCTwKAYcqIYzv](https://www.youtube.com/watch?v=NYxHmck_GjE&pp=0gcJCTwKAYcqIYzv)
   
2. Kemudian buka miniapp bot telegramnya dan buka menu devtool.
   
3. Klik menu **console** biasanya terdapat disebelah menu **element** dan paste kode javascript berikut

```javascript
copy(decodeURIComponent(sessionStorage.getItem('tapps/launchParams').split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
```

   Kode javascript diatas sudah otomatis mengcopy data akun dan kamu bisa mempastenya di file `data.txt`
    
   Jika kamu mendapatkan teks peringatan / tidak bisa melakukan paste kode diatas, ketik dulu kode berikut

```
allow pasting
```
   Jika sudah, coba ulangi lagi paste kode javascript diatas!

## Diskusi

Jika kamu ada pertanyaan, silahkan bergabung di [sdsproject_chat](https://t.me/sdsproject_chat)

## Terima kasih