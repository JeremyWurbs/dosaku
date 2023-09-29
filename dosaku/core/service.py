from dosaku import Module


class Service(Module):
    @property
    def is_service(self):
        return True
