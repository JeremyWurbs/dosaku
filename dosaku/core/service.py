from dosaku import Module


class Service(Module):
    def __init__(self):
        super().__init__()

    @property
    def is_service(self):
        return True
