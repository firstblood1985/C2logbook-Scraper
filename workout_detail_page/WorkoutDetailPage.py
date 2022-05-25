from models.Page import Page


class WorkoutDetailPage(Page):
    ##https://log.concept2.com/profile/1043029/log/62645132
    ##two ways to construct workout detail
    ##1. given workout link directly
    ##2. given profile id and log id

    def __init__(self,*args,**kwargs):
        base_url = 'https://log.concept2.com'
        super().__init__(base_url)
        self.url = None
        self.profile_id = None
        self.log_id = None
        if kwargs.get('workout_link',None):
            self.url = kwargs.get('workout_link').strip('\n')
            self.log_id = self.url.split('/')[-1].strip('\n')
            self.profile_id= self.url.split('/')[-3]
        else:
            self.profile_id = kwargs.get('profile_id')
            self.log_id = kwargs.get('log_id')
            self.url = self.get_url_string()


    def get_url_string(self) -> str:

        return '/'.join([self.base_url,'profile',self.profile_id,'log',self.log_id])

    def __str__(self):
        return "WorkoutDetailPage: [ url: {} ]".format(self.url)
