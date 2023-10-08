import subprocess

from dosaku import Config, Module


class Sabaki(Module):
    name = 'Sabaki'
    config = Config()

    def __init__(self):
        self.process = None

    def start(self, **kwargs):
        """Start the Sabaki GUI."""
        sabaki_path = self.config['APPS']['SABAKI_PATH']
        self.process = subprocess.Popen([sabaki_path, ''])

    def stop(self):
        """Stop and close the Sabaki GUI."""
        if self.process is not None:
            self.process.kill()

    def __call__(self, *args, **kwargs):
        self.start(**kwargs)


Sabaki.register_action('start')
Sabaki.register_action('stop')
Sabaki.register_action('__call__')
Sabaki.register_task('Sabaki')
