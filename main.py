import os
import sys
import json
import httpx
import random
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
    auth = "https://gift-api.stepcdn.space/auth/new"
    refresh = "https://gift-api.stepcdn.space/auth/refresh"
    state = "https://gift-api.stepcdn.space/game2048/1/state"
    spawn = "https://gift-api.stepcdn.space/game2048/1/spawn"
    merge = "https://gift-api.stepcdn.space/game2048/cells/merge"
    daily = "https://gift-api.stepcdn.space/wrapquests?tag=gift_quests_daily"
    epic = "https://gift-api.stepcdn.space/wrapquests?tag=gift_quests_epic"
    main_progress = "https://gift-api.stepcdn.space/wrapquests?tag=gift_main_progress&no_ord_done=true"
    resource = "https://gift-api.stepcdn.space/inventory/resources"
    collect = "https://gift-api.stepcdn.space/wrapquests/collect"
    game_inventory = "https://gift-api.stepcdn.space/inventory?include=game2048_item&include=game2048_field_cell"
    place = "https://gift-api.stepcdn.space/game2048/cells/{}/place"
    burn = "https://gift-api.stepcdn.space/game2048/cells/{}/burn"
    advent = "https://gift-api.stepcdn.space/wrapquests?tag=gift_advent"


HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en,en-US;q=0.9",
    "authorization": "tma",
    "Connection": "keep-alive",
    "content-type": "application/json",
    "Host": "gift-api.stepcdn.space",
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


def login(ses, user_id, accounts):
    try:
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
        if access_token is None:
            log(f"{red}failed login account,{white} maybe account data has expired !")
            return None
        accounts[user_id] = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "exp_refresh_token": exp_refresh_token,
        }
        with open("accounts.json", "w") as w:
            w.write(json.dumps(accounts, indent=4))
        return access_token
    except json.decoder.JSONDecodeError:
        log(f"{red}failed login account,{white} maybe account data has expired !")
        return None


def renew_token(ses, user_id, accounts):
    try:
        res = ses.post(url=URL.refresh, data="")
        if res is None:
            return "bad_proxy"
        access_token = res.json().get("access_token")
        refresh_token = res.json().get("refresh_token")
        exp_refresh_token = res.json().get("refresh_token_expiry")
        if access_token is None:
            log(f"{red}failed{white} to renew access token !")
            return "failed_renew"
        accounts[user_id] = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "exp_refresh_token": exp_refresh_token,
        }
        with open("accounts.json", "w") as w:
            w.write(json.dumps(accounts, indent=4))
        return access_token
    except json.decoder.JSONDecodeError:
        log(f"{red}failed{white} renew access token !")
        return "failed_renew"


def main_progress(ses):
    log(f"{yellow}check{white} main progress !")
    while True:
        res = http(ses=ses, url=URL.main_progress)
        if res is None:
            return "bad_proxy"
        rewards = res.json()
        for index in range(99, -1, -1):
            reward = rewards[index]
            title = reward.get("title")
            state = reward.get("state")
            reward_id = reward.get("uuid")
            current_progress = reward.get("progress", {}).get("current")
            target_progress = reward.get("progress", {}).get("target")
            if current_progress >= target_progress:
                if state == "done":
                    continue
                if state == "completed":
                    log(f"{green}reward{white} {title}, {green}state{white} {state}")
                    ses.headers.update({"x-request-id": reward_id})
                    # print(ses.headers)
                    res = http(ses=ses, url=URL.collect, data="")
                    ses.headers.pop("x-request-id")
                    result = res.json().get("result")
                    if result:
                        log(f"{green}success{white} claim reward !")
                        break
                    else:
                        log(f"{red}failed{white} claim reward !")
            else:
                log(f"{green}reward{white} {title}, {green}state{white} {state}")
                log(
                    f"{green}current progress{white} {current_progress}/{target_progress}"
                )
                return


def advent_progress(ses):
    log(f"{yellow}check{white} advent progress !")
    while True:
        res = http(ses=ses, url=URL.advent)
        if res is None:
            return "bad_proxy"
        rewards = res.json()
        for i in range(30):
            reward = rewards[i]
            reward_id = reward.get("uuid")
            state = reward.get("state")
            title = reward.get("title")
            if state == "completed":
                ses.headers.update({"x-request-id": reward_id})
                res = http(ses=ses, url=URL.collect, data="")
                ses.headers.pop("x-request-id")
                result = res.json().get("result")
                if result:
                    log(f"{green}success{white} collect reward {title}")
                    break
                else:
                    log(f"{red}failed{white} collect reward {title}")
        return


def daily_progress(ses):
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
    ses = httpx.Client(proxy=proxy, http2=True)
    if refresh_token is None:
        log(f"{yellow}refresh token{white} not found !")
        HEADERS["authorization"] = f"tma {query}"
        ses.headers.update(HEADERS)
        access_token = login(ses=ses, user_id=user_id, accounts=accounts)
        if access_token is None:
            return "failed_login"
    if token_is_expired(access_token):
        log(f"{yellow}access token expired{white}, renew access token !")
        HEADERS["authorization"] = f"Bearer {refresh_token}"
        ses.headers.update(HEADERS)
        access_token = renew_token(ses=ses, user_id=user_id, accounts=accounts)
        if access_token == "failed_renew":
            log(f"{yellow}try login{white} with query data !")
            HEADERS["authorization"] = f"tma {query}"
            ses.headers.update(HEADERS)
            access_token = login(ses=ses, user_id=user_id, accounts=accounts)
            if access_token is None:
                return "failed_login"

    HEADERS["authorization"] = f"Bearer {access_token}"
    ses.headers.update(HEADERS)
    main_progress(ses=ses)
    advent_progress(ses=ses)
    daily_progress(ses=ses)
    game_cell = []
    empty_cell = 0
    spawn_amount = 0
    empty_cell_id = []
    first = True
    empty_cell_count = 0
    while True:
        res = http(ses=ses, url=URL.state)
        for cell in res.json().get("cells"):
            item = cell.get("item")
            if item is None:
                empty_cell += 1
                cell_id = cell.get("id")
                empty_cell_id.append(cell_id)
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
        if empty_cell_count >= 4:
            for c in game_cell[0:5]:
                cell_id = c.get("id")
                res = http(ses=ses, url=URL.burn.format(cell_id), data="")
                log(f"{yellow}burn{white} cell id {green}{cell_id}")
            empty_cell_count = 0
            continue

        if empty_cell == 0:
            empty_cell_count += 1

        if empty_cell != 0:
            res = http(ses=ses, url=URL.game_inventory)
            inventory = res.json().get("inventory")
            if len(inventory) != 0:
                for iindex in range(0, len(inventory), +1):
                    iitem = inventory[iindex]
                    iitem_id = iitem["id"]
                    cell_id = random.choice(empty_cell_id)
                    place_data = {"inventory_item_id": iitem_id}
                    res = http(
                        ses=ses,
                        url=URL.place.format(cell_id),
                        data=json.dumps(place_data),
                    )
                    log(
                        f"{green}place item id{white} {iitem_id} {green}to cell id{white} {cell_id}"
                    )
                empty_cell = 0
                spawn_amount = 0
                empty_cell_id = []
                continue
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
                if result == "failed_login":
                    p += 1
                    break
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
