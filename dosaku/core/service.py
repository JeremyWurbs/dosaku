from dosaku import Module


class Service(Module):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def is_service(self):
        return True
