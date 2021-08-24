from pixivpy3 import *

import os
import re
import json
import requests


def search(api,
           word: str):
    print("search({})".format(word))

    response = api.search_novel(word)

    return response["novels"]


def search_text(api,
                word: str):
    print("search_text({})".format(word))

    response = api.search_novel(word, search_target="text")

    return response["novels"]


def process_search(api: AppPixivAPI,
                   searchwords: dict,
                   readed: list,
                   config: dict,
                   init: bool,
                   key: str,
                   func):
    print("process_search({})".format(key))
    for word in searchwords[key]:
        results = func(api, word)
        for result in results:
            novelId = result["id"]

            if novelId in readed:
                continue

            novelTitle = result["title"]
            novelDate = result["create_date"].replace(
                "T", " ").replace("+09:00", "")
            novelTags = list(map(lambda x: x["name"], result["tags"]))
            novelCaption = result["caption"]
            novelCaption = novelCaption.replace("<br />", "\n")
            novelCaption = re.sub(r"<strong>(.*)</strong>",
                                  r"**\1**", novelCaption)
            novelCaption = re.sub(
                r"<a href=\"(.*?)\".*?>(.*?)</a>", r"[\2](\1)", novelCaption)
            novelUsername = result["user"]["name"]

            readed.append(novelId)

            muted = False
            for mutetag in searchwords["mutetags"]:
                if mutetag in novelTags:
                    muted = True
                    break
            if muted:
                continue

            embed = {
                "title": "`{word}` -> `{title}`".format(word=word, title=novelTitle, username=novelUsername),
                "type": "rich",
                "url": "https://www.pixiv.net/novel/show.php?id={id}".format(id=novelId),
                "description": novelCaption,
                "fields": [
                    {
                        "name": "Tags",
                        "value": "`{}`".format("`・`".join(novelTags))
                    },
                    {
                        "name": "Author",
                        "value": "`{}`".format(novelUsername)
                    },
                    {
                        "name": "Date",
                        "value": novelDate
                    }
                ],
                "footer": {
                    "text": "Search type: " + key
                }
            }

            if not init:
                sendMessage(config["discord_channel"], "", embed)

    return readed


def sendMessage(channelId: str,
                message: str = "",
                embed: dict = None):
    if not os.path.exists("config.json"):
        print("config.json not found.")
        exit(1)

    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    print("[INFO] sendMessage: {message}".format(message=message))
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bot {token}".format(token=config["discord_token"]),
        "User-Agent": "Bot"
    }
    params = {
        "content": message,
        "embed": embed
    }
    response = requests.post(
        "https://discord.com/api/channels/{channelId}/messages".format(channelId=channelId), headers=headers,
        json=params)
    print("[INFO] response: {code}".format(code=response.status_code))
    print("[INFO] response: {message}".format(message=response.text))


def main():
    if not os.path.exists("config.json"):
        print("config.json not found.")
        exit(1)

    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    if not os.path.exists("searchwords.json"):
        print("searchwords.json not found.")
        exit(1)

    with open("searchwords.json", "r", encoding="utf-8") as f:
        searchwords = json.load(f)

    api = AppPixivAPI()
    if os.path.exists("token.json"):
        with open("token.json", "r", encoding="utf-8") as f:
            token = json.load(f)
            token = api.auth(None, None, token["refresh_token"])
            with open("token.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(token))
    else:
        token = api.login(config.get("username"), config.get("password"))
        with open("token.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(token))

    readed = []
    init = True
    if os.path.exists("data.json"):
        print("[INFO] Usual mode")
        init = False
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        readed = data["readed"]

        if searchwords["words"] != data["searchwords"]:
            init = True
            print("[INFO] Initialize mode (Changed searchwords)")

        if searchwords["textwords"] != data["textwords"]:
            init = True
            print("[INFO] Initialize mode (Changed textwords)")
    else:
        print("[INFO] Initialize mode")

    # -------------
    process_search(api, searchwords, readed, config, init, "words", search)
    process_search(api, searchwords, readed, config, init, "textwords", search_text)

    print(readed)

    with open("data.json", "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "readed": readed,
            "searchwords": searchwords["words"],
            "textwords": searchwords["textwords"]
        }))


if __name__ == "__main__":
    if not os.path.exists("config.json"):
        print("config.json not found.")
        exit(1)
    main()
