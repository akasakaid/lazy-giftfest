import os
import sys
import json
import httpx
from utils import http, log, parse_query_data, token_is_expired, countdown
from collections import defaultdict
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)

green = Fore.LIGHTGREEN_EX
red = Fore.LIGHTRED_EX
reset = Style.RESET_ALL
yellow = Fore.LIGHTYELLOW_EX
white = Fore.LIGHTWHITE_EX


class URL:
    auth = "https://gift.stepcdn.space/auth/new"
    refresh = "https://gift.stepcdn.space/auth/refresh"
    state = "https://gift.stepcdn.space/game2048/1/state"
    spawn = "https://gift.stepcdn.space/game2048/1/spawn"
    merge = "https://gift.stepcdn.space/game2048/cells/merge"
    daily = "https://gift.stepcdn.space/wrapquests?tag=gift_quests_daily"
    epic = "https://gift.stepcdn.space/wrapquests?tag=gift_quests_epic"
    main_progress = (
        "https://gift.stepcdn.space/wrapquests?tag=gift_main_progress&no_ord_done=true"
    )
    resource = "https://gift.stepcdn.space/inventory/resources"
    collect = "https://gift.stepcdn.space/wrapquests/collect"


HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en,en-US;q=0.9",
    "authorization": "tma ",
    "Connection": "keep-alive",
    "content-type": "application/json",
    "Host": "gift.stepcdn.space",
    "Origin": "https://gift-static.stepcdn.space",
    "Referer": "https://gift-static.stepcdn.space/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.61 Mobile Safari/537.36 Telegram-Android/12.2.7 (Asus ASUSAI2501B; Android 12; SDK 32; AVERAGE)",
    "X-Platform": "android",
    "X-Requested-With": "org.telegram.messenger",
    "X-Service-Name": "gift",
    "X-Timezone-Offset": "-420",
}


def myaku(query, proxy=None):
    query_data = parse_query_data(query)
    user_id = query_data.get("user", {}).get("id")
    if user_id is None:
        log(
            f"{yellow}user_id {white}not found. Your query format/data may be incorrect !"
        )
        return
    user_id = str(user_id)
    first_name = query_data.get("user", {}).get("first_name")
    log(f"{green}using account query data {white}{first_name}")
    with open("accounts.json") as r:
        accounts = json.loads(r.read())
    user_data = accounts.get(user_id, {})
    refresh_token = user_data.get("refresh_token")
    access_token = user_data.get("access_token")
    ses = httpx.Client(proxy=proxy)
    if refresh_token is None:
        log(f"{yellow}refresh token{white} not found !")
        HEADERS["authorization"] = f"tma {query}"
        ses.headers.update(HEADERS)
        res = http(
            ses=ses,
            url=URL.auth,
            data=json.dumps(
                {
                    "referral_code": "000000gb3b2",
                    "referral_source": "invite_friend",
                    "utm_source": "invite_friend",
                }
            ),
        )
        if res is None:
            return "bad_proxy"
        access_token = res.json().get("access_token")
        refresh_token = res.json().get("refresh_token")
        exp_refresh_token = res.json().get("refresh_token_expiry")
        accounts[user_id] = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "exp_refresh_token": exp_refresh_token,
        }
        with open("accounts.json", "w") as w:
            w.write(json.dumps(accounts, indent=4))
    if token_is_expired(access_token):
        log(f"{yellow}access token expired{white}, renew access token !")
        HEADERS["authorization"] = f"Bearer {refresh_token}"
        ses.headers.update(HEADERS)
        res = ses.post(url=URL.refresh, data="")
        if res is None:
            return "bad_proxy"
        access_token = res.json().get("access_token")
        refresh_token = res.json().get("refresh_token")
        exp_refresh_token = res.json().get("refresh_token_expiry")
        accounts[user_id] = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "exp_refresh_token": exp_refresh_token,
        }
        with open("accounts.json", "w") as w:
            w.write(json.dumps(accounts, indent=4))
    HEADERS["authorization"] = f"Bearer {access_token}"

    ses.headers.update(HEADERS)
    game_cell = []
    empty_cell = 0
    spawn_amount = 0
    first = True
    while True:
        res = http(ses=ses, url=URL.state)
        for cell in res.json().get("cells"):
            item = cell.get("item")
            if item is None:
                empty_cell += 1
                continue
        game_cell = res.json().get("cells")
        res = http(ses=ses, url=URL.resource)
        resources = res.json().get("resources")
        user_res = {}
        for resource in resources:
            amount = resource.get("amount")
            name = resource.get("slug")
            log(f"{amount} {name}")
            user_res[name] = amount
        if not first:
            if user_res.get("energy") < 5:
                return (20 - user_res.get("energy")) * 600
        log(f"{green}total empty cell{white} {empty_cell}")
        if empty_cell != 0:
            log(f"try to spawn {green}{empty_cell}{white} item")
            log("check remaining energy to spawn !")
            _spawn_amount = user_res.get("energy") / 5
            if _spawn_amount >= empty_cell:
                log(f"{green}enough{white} energy to spawn !")
                spawn_amount = empty_cell
            else:
                log(f"{yellow}insufficient{white} energy to spawn !")
                log(f"spawn count changed to {green}{int(_spawn_amount)}")
                spawn_amount = int(_spawn_amount)
            for _ in range(spawn_amount):
                res = http(ses=ses, url=URL.spawn, data="")
                if res is None:
                    return "bad_proxy"
                updated_cells = res.json().get("updated_cells")
                if updated_cells is None:
                    continue
                if len(updated_cells) == 0:
                    log(f"{red}failed{white} to spawn ({_ + 1}) !")
                    continue
                _item_name = updated_cells[0]["item"]["title"]
                _item_rarity = updated_cells[0]["item"]["rarity"]
                log(
                    f"{green}get{white} item {green}{_item_name}{white} rarity{green} {_item_rarity}"
                )
                game_cell = res.json().get("field", {}).get("cells")
            empty_cell = 0
            spawn_amount = 0
        log(f"{yellow}start{white} merge items !")
        groups = defaultdict(list)
        for cell in game_cell:
            cell_id = cell.get("id")
            item = cell.get("item")
            if item is None:
                continue
            item_id = item.get("id")
            groups[item_id].append(cell_id)
        results = [ids[:2] for ids in groups.values() if len(ids) >= 2]
        for result in results:
            log(
                f"{yellow}try{white} merge cell id {green}{result[0]}{white} with {green}{result[1]}"
            )
            merge_data = {"cell_ids": result}
            res = http(ses=ses, url=URL.merge, data=json.dumps(merge_data))
            updated_cells = res.json().get("updated_cells")
            if len(updated_cells) == 0:
                log(f"{red}failed{white} do merge cells !")
                continue
            for uc in updated_cells:
                burn_reward = uc.get("burn_rewards")
                if burn_reward is None:
                    continue
                _item_name = uc.get("item", {}).get("title")
                _item_rarity = uc.get("item", {}).get("rarity")
                log(
                    f"{green}merge{white} result {green}gets{white} item {green}{_item_name}{white} rarity {green}{_item_rarity}"
                )
            game_cell = res.json().get("field", {}).get("cells")
        # daily quest
        log(f"{yellow}check{white} daily quests !")
        res = http(ses=ses, url=URL.daily)
        if res is None:
            return "bad_proxy"
        for rew in res.json():
            reward_id = rew.get("uuid")
            reward_state = rew.get("state")
            reward_title = rew.get("title")
            log(f"{green}{reward_title}{white} status {reward_state}")
            if reward_state == "completed":
                ses.headers.update({"x-request-id": reward_id})
                res = http(ses=ses, url=URL.collect, data="")
                if res is None:
                    return "bad_proxy"
                is_true = res.json().get("result")
                if not is_true:
                    log(f"{red}failed{white} claim quest reward !")
                    continue
                for _reward in res.json().get("rewards"):
                    _rew_title = _reward.get("slug")
                    _rew_amount = _reward.get("real_amount")
                    log(f"{green}get{white} {_rew_amount} {_rew_title}")
        first = False


def main():
    os.system("cls" if os.name == "nt" else "clear")
    print(f"""

{green}script{white} for auto merge @giftfest_bot
          
join {green}@sdsproject{white} for more !

""")
    if not os.path.exists("accounts.json"):
        open("accounts.json", "w").write("{}")
    require_files = ["data.txt", "proxies.txt"]
    for reqfile in require_files:
        if not os.path.exists(reqfile):
            open(reqfile, "a")
    datas = open("data.txt").read().splitlines()
    proxies = open("proxies.txt").read().splitlines()
    print(f"{green}total account{white} : {len(datas)}")
    print(f"{green}total proxy{white} : {len(proxies)}")
    print()
    print()
    p = 0
    results = []
    while True:
        for data in datas:
            print("~" * 50)
            while True:
                proxy = None if len(proxies) == 0 else proxies[p % len(proxies)]
                if proxy is None:
                    proxy = None
                else:
                    if len(proxy) < 5:
                        proxy = None
                result = myaku(query=data, proxy=proxy)
                if result == "bad_proxy":
                    log(f"{yellow}proxy{white} is {red}bad !")
                    p += 1
                    continue
                if result is None:
                    break
                if isinstance(result, int):
                    results.append(result)
                    p += 1
                    break
        _min = min(results)
        countdown(_min)
        results = []


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
