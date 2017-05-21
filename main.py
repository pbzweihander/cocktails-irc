
from irc import *
from cocktaildb import *

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

                handle(chan, msg)


def handle(chan: str, msg: str):
    s = ''
    if msg.startswith('c?'):
        name = msg.split('?')[1].strip()
        if name:
            if name == 'random':
                s = random_cocktails()
            else:
                s = find_cocktails(name)
            if not s:
                s = '._.'
    elif msg.startswith('cs?'):
        name = msg.split('?')[1].strip()
        if name:
            s = find_cocktails(name, True)
            if not s:
                s = '._.'
    elif msg.startswith('i?'):
        name = msg.split('?')[1].strip()
        if name:
            s = find_ingredient(name)
            if not s:
                s = '._.'
    elif msg.startswith('is?'):
        name = msg.split('?')[1].strip()
        if name:
            s = find_ingredient(name, True, False)
            if not s:
                s = '._.'
    elif msg.startswith('id?'):
        name = msg.split('?')[1].strip()
        if name:
            s = find_ingredient(name, False, True)
            if not s:
                s = '._.'
    if s:
        if '\n' in s:
            for l in s.split('\n'):
                irc.send(chan, l)
        else:
            irc.send(chan, s)


if __name__ == '__main__':
    main()
