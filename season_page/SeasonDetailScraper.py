from collections.abc import Iterable

from models.Scraper import Scraper
from season_page.SeasonDetailPage import SeasonDetailPage
from common.Utils import *


class SeasonDetailScraper(Scraper):
    def __init__(self):
        super().__init__()
        pass

    def get_config_key(self):
        return 'season_detail'

    def init_from_config(self, config, session=None,cnx=None,username=''):
        self.cnx = cnx
        self.session = session
        self.base_url = 'https://log.concept2.com/season'
        self.years = config['years']
        self.username = username
        self.workout_details_dir = config['workout_details_dir']
        self.workout_detail_meta_file = config['workout_details_meta_file']
        self.use_softlink = config['use_softlink']
        self.season_detail_pages=[]

        for year in self.years:
            self.season_detail_pages.append(SeasonDetailPage(self.base_url, year, self.username))

        self.workout_detail_meta_file = '/'.join(
            [self.workout_details_dir, self.workout_detail_meta_file]) + '_'+self.username+'_' + today()

        if self.use_softlink:
            self.link_workout_details_file = '/'.join([self.workout_details_dir, config['workout_details_meta_file']])+'_'+self.username
            self.source_workout_details_file = config['workout_details_meta_file'] + '_' +self.username+'_'+ today()

    def scrape(self):
        if not self.season_detail_pages:
            print("there are no season details to scrape, please configure properly")
            quit()

        self.data = {}
        for season_detail_page in self.season_detail_pages:
            print("processing: "+str(season_detail_page))
            r = self.get_url(self.session, season_detail_page.url)
            if r:
                season_detail_page.set_data(self.scrape_page_details(r.text))
                self.data[season_detail_page.get_key()] = season_detail_page.get_key()
                workout_links = self.get_workout_links(season_detail_page.get_data())
                self.write_array_result_to_file(workout_links, self.workout_detail_meta_file)
                if self.use_softlink:
                    self.link(self.source_workout_details_file, self.link_workout_details_file)

        ##input data into workout details file

    def get_workout_links(self,data):
        workout_links = []
        for workout in data:
            workout_links.append(workout[-1])
        return workout_links

    def scrape_page_details(self, text) -> Iterable:
        results = []
        for row in self.scrape_table_detail_by_text(text):
            if row:
                workout_link = row.xpath(r'td/a')[0].attrib['href']
                workout_edit_link = row.xpath(r'td/a')[1].attrib['href']
                result = [c.text for c in row.xpath(r'td')]
                result.extend([workout_link])
                results.append(result)

        return results
