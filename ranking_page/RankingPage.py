from models.Page import Page


class RankingPage(Page):
    def __init__(self,base_url,machine,year,event,query_params = {}):
        super().__init__(base_url)
        self.machine = machine
        self.year = year
        self.event = event
        self.query_parms = query_params
        self.url = self.get_url_string()

    def get_url_string(self) -> str:
        ##https://log.concept2.com/rankings/2022/rower/1
        url_string = '/'.join([self.base_url,self.year,self.machine,str(self.event)])
        if self.query_parms:
            url_string +'?'
            for k,v in self.query_parms:
                if k and v:
                    url_string += k +'=' + v +'&'
            return url_string.strip('&')
        else:
            return url_string

    def get_key(self) -> str:
        return '#'.join(self.year,self.machine,str(self.event))

