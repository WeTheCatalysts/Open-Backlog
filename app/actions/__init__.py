from data import DefaultProvider as Provider

class Backlog():

    def __init__(self, config):
        self.__config = config

    def get_backlog(self):
        return Provider(self.__config).fetch_backlog()
