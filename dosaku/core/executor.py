from dosaku import Module


class Executor(Module):
    def __init__(self):
        super().__init__()

    @property
    def is_executor(self):
        return True
