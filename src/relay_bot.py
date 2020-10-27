#!/usr/bin/env python3
import asyncio, re
from argparse  import ArgumentParser
from typing    import Dict, List, Optional

from irctokens import build, Line
from ircrobots import Bot    as BaseBot
from ircrobots import Server as BaseServer
from ircrobots import ConnectionParams

TRIGGER = "!"
botname="botsix"

class Bot(BaseBot):
    def __init__(self, channel1: str, channel2: str):
        super().__init__()
        self._channel1 = channel1
        self._channel2 = channel2
    def create_server(self, name: str):
        return Server(self, name, self._channel1, self._channel2)

class Server(BaseServer):
    def __init__(self, bot: Bot, name: str, channel1: str, channel2: str):
        super().__init__(bot, name)
        self._channel1 = channel1
        self._channel2 = channel2

    async def line_send(self, line: Line):
        print(f"> {line.format()}")

    async def line_read(self, line: Line):
        print(f"< {line.format()}")

        me = self.nickname_lower
        if line.command == "001":
            await self.send(build("JOIN", [self._channel1]))
            await self.send(build("JOIN", [self._channel2]))

        if (
                line.command == "PRIVMSG" and
                self.has_channel(line.params[0]) and
                not line.hostmask is None and
                not self.casefold(line.hostmask.nickname) == me and
                self.has_user(line.hostmask.nickname) and
#                line.params[1].startswith(TRIGGER)):
                True):

            if line.params[0]==self._channel1: channel12=self._channel2
            elif line.params[0]==self._channel2: channel12=self._channel1

            channel = self.channels[self.casefold(line.params[0])]
            user    = self.users[self.casefold(line.hostmask.nickname)]
            cuser   = channel.users[user.nickname_lower]
            text    = line.params[1].replace(TRIGGER, "", 1)

            #action, _, text = text.partition(" ")

            out = f"<{user.nickname}> {text}" if text[0]!="\x01" else f"* {user.nickname} {text}"
            #await self.send(build("PRIVMSG", [line.params[0], out]))
            await self.send(build("PRIVMSG", [channel12, out]))

async def main(hostname: str, channel1: str, channel2: str, nickname: str):
    bot = Bot(channel1,channel2)

    params = ConnectionParams(
        nickname,
        hostname,
        6697,
        tls=True)
    await bot.add_server("~chat", params)
    await bot.run()

if __name__ == "__main__":
    parser = ArgumentParser(description="A simple IRC bot for jan6")
    parser.add_argument("--hostname",default="tilde.chat")
    parser.add_argument("-n","--nickname",default=botname)
    parser.add_argument("channel1")
    parser.add_argument("channel2")
    args = parser.parse_args()

#    asyncio.run(main(args.hostname, args.channel, args.nickname))
    asyncio.run(main(args.hostname, args.channel1, args.channel2, args.nickname))
