import random

from dosaku import Config
from dosaku.modules.go.gtp_v1 import GoTextProtocolV1Helper


class RandomGoBot(GoTextProtocolV1Helper):
    name = 'RandomGoBot'
    bot_version = '1.0'
    config = Config()

    def __init__(self, boardsize=19):
        super().__init__()
        self._boardsize = boardsize

    def version(self):
        return self.bot_version

    def list_commands(self):
        return 'protocol_version'

    def quit(self):
        pass

    def komi(self, komi: float) -> None:
        pass

    def boardsize(self, size: int) -> None:
        self._boardsize = size

    def clear_board(self) -> None:
        pass

    def play(self, player: str, move: str) -> None:
        pass

    def genmove(self, player: str) -> str:
        row_names = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'
        row = random.randint(1, self._boardsize)
        col = random.randint(1, self._boardsize)
        row_str = row_names[row]
        col_str = str(col)
        return row_str + col_str


RandomGoBot.register_task('GoTextProtocolV1')

if __name__ == "__main__":
    bot = RandomGoBot()
    while True:
        command = input()
        print(bot.handle_command(command, suffix='\n'))
