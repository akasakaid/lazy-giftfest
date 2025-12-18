# Lazy-GiftFest

Auto play / auto merge for the **@giftfest** Telegram game bot.

## Features

* Auto merge / Auto Play
* Daily checkin
* Checking daily tasks

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

## Discussion

If you have any questions, feel free to join the discussion at
[sdsproject_chat](https://t.me/sdsproject_chat)

## Thank You

