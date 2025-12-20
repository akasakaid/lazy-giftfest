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
    print()