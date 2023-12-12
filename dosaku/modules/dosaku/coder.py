from dosaku import Executor, Service


class Coder(Executor, Service):
    name = 'Coder'

    def __init__(self, **_):
        super().__init__()
        print(f'Coder.is_executor: {self.is_executor}')
        print(f'Coder.is_service: {self.is_service}')
