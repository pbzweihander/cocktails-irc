
from irc import *
import requests
import json

channel = "#pbzweihander"
server = "irc.uriirc.org"
port = 16664
nickname = "bartender-bot"

irc = IRC()


def main():
    global irc

    irc.init()
    irc.connect(server, port, channel, nickname)

    while True:
        lines = irc.get_text()

        for text in lines:
            if not text:
                continue

            if 'PING ' in text:  # 서버에서 핑 요청시 응답
                irc.raw_send('PONG ' + text.split()[1])

            if 'INVITE ' in text:  # 유저가 채널로 초대시 응답
                irc.join(text.split(':', 2)[-1])

            print("[r] " + text)  # 로그

            if 'PRIVMSG ' in text:
                chan = text.split("PRIVMSG ")[1].split()[0]
                sender = text.split("!")[0][1:]
                msg = text.split(":", 2)[2]

                if "#" not in chan:  # 채널 메세지가 아니라 쿼리(귓속말)
                    chan = sender

                ss = handle(msg)
                if ss:
                    for s in ss:
                        if s:
                            irc.send(chan, s)


def handle(msg: str) -> tuple:
    if msg[:2] == 'c>':
        name = msg.split('>')[1].strip()
        if name:
            if name == 'random':
                return random_cocktails()
            else:
                return find_cocktails(name)
    elif msg[:2] == 'i>':
        name = msg.split('>')[1].strip()
        if name:
            return find_ingredient(name)
    return ()


def find_cocktails(name: str) -> tuple:
    dlist = get_drinklist(r"http://www.thecocktaildb.com/api/json/v1/1/search.php?s=" + name)
    if dlist[0].get('strDrink').strip().lower() == name.lower():
        return parse_cocktail(dlist[0])
    else:
        nlist = [d.get('strDrink') for d in dlist]
        if len(nlist) < 8:
            return ', '.join(nlist),
        else:
            return ', '.join(nlist[:8]),


def random_cocktails() -> tuple:
    dlist = get_drinklist(r"http://www.thecocktaildb.com/api/json/v1/1/random.php")
    d = dlist[0]
    return parse_cocktail(d)


def parse_cocktail(d: dict) -> tuple:
    name = d.get('strDrink').strip()
    if not name:
        return ()
    glass = (d.get('strGlass') or "").strip()
    ingredients = []
    measures = []
    for i in range(1, 16):
        ii = d.get("strIngredient%s" % i).strip()
        mm = d.get("strMeasure%s" % i).strip()
        if len(ii) > 0 and len(mm) > 0:
            ingredients.append(ii)
            measures.append(mm)
    instruction = (d.get("strInstructions") or "").strip()
    s = name + '\n'
    if glass:
        s += 'Serve on : ' + glass + '\n'
    for i, m in zip(ingredients, measures):
        s += i + ' - ' + m + '\n'
    s += instruction
    return tuple(s.split('\n'))


def get_drinklist(url: str) -> list:
    r = requests.get(url)
    if len(r.text) > 0:
        dl = json.loads(r.text).get('drinks')
        if dl:
            return list(dl)
    return []


def find_ingredient(name: str) -> tuple:
    dlist = get_ingredientlist(r"http://www.thecocktaildb.com/api/json/v1/1/search.php?i=" + name)
    if not dlist:
        return ()
    if dlist[0].get('strIngredient').strip().lower() == name.lower():
        return parse_ingredient(dlist[0])
    else:
        nlist = [d.get('strIngredient') for d in dlist]
        if len(nlist) < 8:
            return ', '.join(nlist),
        else:
            return ', '.join(nlist[:8]),


def parse_ingredient(d: dict) -> tuple:
    print(d)
    name = d.get('strIngredient').strip()
    if not name:
        return ()
    stype = (d.get('strType') or "").strip()
    description = (d.get("strDescription") or "").strip()
    s = name + '\n'
    if stype:
        s += 'Type : ' + stype + '\n'
    s += description
    return tuple(s.split('\n'))


def get_ingredientlist(url: str) -> list:
    r = requests.get(url)
    if len(r.text) > 0:
        il = json.loads(r.text).get('ingredients')
        if il:
            return list(il)
    return []


if __name__ == '__main__':
    main()
