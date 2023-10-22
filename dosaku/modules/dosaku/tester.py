from dosaku import Executor


class Tester(Executor):
    """Test code."""
    name = 'Tester'

    def __init__(self):
        super().__init__()


Tester.register_action('exec')
Tester.register_task('Tester')
