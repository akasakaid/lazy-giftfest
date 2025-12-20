# Lazy-GiftFest

Auto play / auto merge for the **@giftfest** Telegram game bot.

## Features

* Auto merge / Auto Play
* Daily checkin
* Checking daily tasks
* Claim rewards / join the draw in the main quest

## How to Use

Make sure your computer has **Python** and **Git** installed.

```bash
git clone https://github.com/akasakaid/lazy-giftfest.git
cd lazy-giftfest
python -m pip install -r requirements.txt
```

Create the files `data.txt` and `proxies.txt`.

Obtain your account query data and paste it into the `data.txt` file.
Each line should contain **one account query**.

Example content of `data.txt`:

```
query_id=123......
query_id=456......
query_id=789......
```

If you want to use a proxy, fill in the `proxies.txt` file using the following format:

**With authentication:**

```
http://user:password@proxy_ip:port
```

**Without authentication:**

```
http://proxy_ip:port
```

After everything is set up, run `main.py`:

```bash
python main.py
```

## How to Get Account Query Data

1. You need to enable **DevTools** in the Telegram Desktop application.
   You can watch this video tutorial:
   [https://www.youtube.com/watch?v=NYxHmck_GjE&pp=0gcJCTwKAYcqIYzv](https://www.youtube.com/watch?v=NYxHmck_GjE&pp=0gcJCTwKAYcqIYzv)

2. Open the Telegram bot mini app, then open the **DevTools** menu.

3. Click the **Console** tab (usually located next to the **Elements** tab), then paste the following JavaScript code:

```javascript
copy(decodeURIComponent(sessionStorage.getItem('tapps/launchParams').split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
```

   The JavaScript code above automatically copies the account data and you can paste it into the `data.txt` file.

   If you receive a warning message or are unable to paste the code above, first type the following command:

```
allow pasting
```

   After that, try pasting the JavaScript code again.


## Discussion

If you have any questions, feel free to join the discussion at
[sdsproject_chat](https://t.me/sdsproject_chat)

## Thank You

