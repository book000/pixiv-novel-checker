from pixivpy3 import *

import os
import re
import json
import requests


def search(word: str):
    print("search({})".format(word))
    if not os.path.exists("config.json"):
        print("config.json not found.")
        exit(1)

    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    api = AppPixivAPI()
    api.login(config.get("username"), config.get("password"))

    response = api.search_novel(word)

    return response["novels"]


def sendMessage(channelId: str, message: str = "", embed: dict = None):
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

    readed = []
    init = True
    if os.path.exists("data.json"):
        print("[INFO] Usual mode")
        init = False
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        readed = data["readed"]

        if searchwords != data["searchwords"]:
            init = True
            print("[INFO] Initialize mode (Changed searchwords)")
    else:
        print("[INFO] Initialize mode")

    for word in searchwords:
        results = search(word)
        for result in results:
            novelId = result["id"]

            if novelId in readed:
                continue

            novelTitle = result["title"]
            novelDate = result["create_date"].replace("T", " ").replace("+09:00", "")
            novelTags = list(map(lambda x: x["name"], result["tags"]))
            novelCaption = result["caption"]
            novelCaption = novelCaption.replace("<br />", "\n")
            novelCaption = re.sub(r"<strong>(.*)</strong>", r"**\1**", novelCaption)
            novelCaption = re.sub(r"<a href=\"(.*?)\".*?>(.*?)</a>", r"[\2](\1)", novelCaption)
            novelUsername = result["user"]["name"]

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
                ]
            }

            if not init:
                sendMessage(config["discord_channel"], "", embed)
            readed.append(novelId)

    print(readed)

    with open("data.json", "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "readed": readed,
            "searchwords": searchwords
        }))


if __name__ == "__main__":
    if not os.path.exists("config.json"):
        print("config.json not found.")
        exit(1)
    main()
