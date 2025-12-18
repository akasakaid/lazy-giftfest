import os
import sys
import httpx
import json
import time
from datetime import datetime
from base64 import urlsafe_b64decode
from urllib.parse import parse_qs
from colorama import Fore, Style

black = Fore.LIGHTBLACK_EX
reset = Style.RESET_ALL


def countdown(t):
    for i in range(t, 0, -1):
        minutes, seconds = divmod(i, 60)
        hours, minutes = divmod(minutes, 60)
        seconds = str(seconds).zfill(2)
        minutes = str(minutes).zfill(2)
        hours = str(hours).zfill(2)
        print(f"waiting until {hours}:{minutes}:{seconds}  ", flush=True, end="\r")
        time.sleep(1)


def parse_query_data(query):
    pars = {key: value[0] for key, value in parse_qs(query).items()}
    pars["user"] = json.loads(pars["user"])
    return pars


def token_is_expired(token=None):
    if token is None:
        return True
    header, body, sign = token.split(".")
    debody = urlsafe_b64decode(body + "==")
    dbody = json.loads(debody)
    exp = dbody.get("exp")
    now = datetime.now().timestamp()
    if (now + 300) > exp:
        return True
    return False


def log(msg):
    now = datetime.now().isoformat(" ").split(".")[0]
    print(f"{black}[{now}]{reset} {msg}")


def http(ses: httpx.Client, url: str, data=None):
    for i in range(5):
        try:
            if data is None:
                res = ses.get(url=url)
            elif data == "":
                res = ses.post(url=url)
            else:
                res = ses.post(url=url, data=data)
            if (
                not os.path.exists("http.log")
                or os.path.getsize("http.log") / 1024 > 1024
            ):
                open("http.log", "w").write("")
            with open("http.log", "a", encoding="utf-8") as w:
                w.write(f"{res.status_code} {res.text}\n")
            return res
        except KeyboardInterrupt:
            sys.exit()
        except:  # noqa: E722
            continue


if __name__ == "__main__":
    # print('token is expired :',token_is_expired('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjQ5MjM1MDgsInVzZXJfaWQiOiI2OTU5MzYyMjk0In0.v1CjRMiRthN7Vw9EuWxazTkTCDTn3uVzTGTtw15NdwE'))
    print(
        parse_query_data(
            "user=%7B%22id%22%3A6959362294%2C%22first_name%22%3A%22Samet%20%C5%9Fahin%22%2C%22last_name%22%3A%22%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FdEd38qoLuZRwkyYO75AwJRRpV6ZHWAFk4KY2s6u7s9X5ondJ-o2fNLTQx3ktwN9G.svg%22%7D&chat_instance=-7668059221342750541&chat_type=private&start_param=UkM9MDAwMDAwZ2IzYjImUlM9aW52aXRlX2ZyaWVuZA%3D%3D&auth_date=1764900913&signature=zMeM-Bhz8kOf7BGZ6H9djd3_yXFtBoslbdX3mRikvnDpEUyUxLGN7jG7ih6WIWYZhu_xvOc54iFWzT-z7XRAAA&hash=fbccdfe6ab2b0c6ae684dd675a5846d9b8d3bad280e788d51a4499b479bd3bbd"
        )
    )
