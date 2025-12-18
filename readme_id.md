# Lazy-GiftFest

Auto play/Auto merge game @giftfest telegram bot

## Fitur

* Auto merge / Play game
* Daily check in
* Mengecek daily task

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

## Diskusi

Jika kamu ada pertanyaan, silahkan bergabung di [sdsproject_chat](https://t.me/sdsproject_chat)

## Terima kasih