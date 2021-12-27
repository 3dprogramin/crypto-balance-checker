import logging as log
log.getLogger().setLevel(log.INFO)


class Log:
    def __init__(self, cryptocurrency):
        self.cryptocurrency = cryptocurrency

    def info(self, text):
        log.info(f'[{self.cryptocurrency}] {text}')

    def warning(self, text):
        log.warning(f'[{self.cryptocurrency}] {text}')

    def error(self, text):
        log.error(f'[{self.cryptocurrency}] {text}')
