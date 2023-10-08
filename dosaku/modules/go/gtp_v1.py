from abc import ABC, abstractmethod

from dosaku import Module


class GoTextProtocolV1Helper(Module, ABC):
    """Helper class for a Go Text Protocol V1 Module."""
    name = 'GoTextProtocolV1Helper'

    def handle_command(self, command: str, prefix: str = '= ', suffix: str = '\n'):
        """Handle any valid command given by a string.

        Note on the suffix: GTP v1 expects two newline characters. If you use the python print() command to relay a
        command, it automatically adds an extra newline character. I.e. use '\n\n' to pass the string directly, or
        '\n' if you are using print.

        The following commands should be supported:
            - version
            - protocol_version
            - list_commands
            - quit
            - komi <float>              E.g. "komi 6.5"
            - boardsize <int>           E.g. "boardsize 19"
            - clear_board
            - play <char> <move_str>    E.g. "play B E3"
            - genmove <char>            E.g. "genmove W"

        Note for play and genmove, the char passed in will be either B or W, marking the player to play. In the case of
        play, the move will be given as a row + col string, where row is a letter representing the row, and col is an
        integer representing the column.

        Args:
            command: The command to handle.
            prefix: The prefix to add to the returned string. For GTP v1 the prefix is always '= '.
            suffix: The suffix to add to the returned string. For GTP v1 there must be two newline characters.

        Returns:
            A string response. The content of the string is determined by the specific command.
        """
        if 'name' in command:
            return prefix + self.name + suffix

        elif 'protocol_version' in command:
            return prefix + self.protocol_version() + suffix

        elif 'version' in command:
            return prefix + self.version() + suffix

        elif 'list_commands' in command:
            return prefix + self.list_commands() + suffix

        elif 'boardsize' in command:
            size = int(command.split()[-1])
            self.boardsize(size)
            return prefix + suffix

        elif 'komi' in command:
            komi_ = float(command.split()[-1])
            self.komi(komi=komi_)
            return prefix + suffix

        elif 'genmove' in command:
            player = command.split()[-1]
            return prefix + self.genmove(player) + suffix

        elif 'quit' in command:
            self.quit()

        else:
            return prefix + suffix  # Skip currently unsupported command

    def protocol_version(self):
        return '1'

    @abstractmethod
    def version(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def list_commands(self):
        raise NotImplementedError

    @abstractmethod
    def quit(self):
        raise NotImplementedError

    @abstractmethod
    def komi(self, komi: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def boardsize(self, size: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def clear_board(self):
        raise NotImplementedError

    @abstractmethod
    def play(self, player: str, move: str):
        raise NotImplementedError

    @abstractmethod
    def genmove(self, player: str) -> str:
        raise NotImplementedError
