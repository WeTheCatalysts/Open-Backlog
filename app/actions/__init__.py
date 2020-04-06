from data import DefaultProvider as Provider




class Backlog():

    def __init__(self, api_id, api_password):
        self.__api_id = api_id
        self.__api_password = api_password

    def build_key(self):
        return 'backlog__' + self.__api__id

    def get_backlog(self):
        return Provider(self.__api_id, self.__api_password).fetch_backlog()

    def get_backlog_item(self, id):
        return Provider(self.__api_id, self.__api_password).fetch_backlog_item(id)




class Organisations():

    def __init__(self, api_id, api_password):
        self.__api_id = api_id
        self.__api_password = api_password

    def build_key(self):
        return 'organisations'

    def get_organisations(self):
        return Provider(self.__api_id, self.__api_password).fetch_organisations()
