from collections.abc import Iterable


class Page():
    def __init__(self,base_url):
        self.base_url = base_url

    def get_url_string(self) -> str:
        pass

    def get_key(self) -> str:
        pass

    def set_data(self,data):
        self.data = data

    def get_data(self) -> Iterable :
        return self.data