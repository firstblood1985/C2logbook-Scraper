from models.Page import Page


class SeasonDetailPage(Page):
    def __init__(self,base_url,year,username):
        super().__init__(base_url)
        self.year = year
        self.url = self.get_url_string()
        self.username = username

    def get_url_string(self) -> str:
        #https: // log.concept2.com / season / 2022
        return '/'.join([self.base_url,self.year])

    def get_key(self) -> str:
        return '#'.join([self.username,self.year])

    def __str__(self):
        return "SeasonDetailPage: [year: {}, user: {}, url: {}]".format(self.year,self.username,self.url)




