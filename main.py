
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

                ss, chk = handle(msg)
                if ss:
                    for s in ss:
                        if s:
                            irc.send(chan, s)
                elif not ss and chk:
                    irc.send(chan, "._.")


def handle(msg: str) -> tuple:
    s = ""
    chk = False
    if msg[:2] == 'c?':
        chk = True
        name = msg.split('>')[1].strip()
        if name:
            if name == 'random':
                s = random_cocktails().split('\n')
            else:
                s =  find_cocktails(name)
    elif msg[:2] == 'i?':
        chk = True
        name = msg.split('>')[1].strip()
        if name:
            s = find_ingredient(name)
    if s:
        if '\n' in s:
            return tuple(s.split('\n')), chk
        else:
            return (s, ), chk
    return (), chk


if __name__ == '__main__':
    main()
