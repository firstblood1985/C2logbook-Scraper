from collections.abc import Iterable

from lxml import html

from models.Scraper import Scraper
from ranking_page.RankingPage import RankingPage

class RankingPageScraper(Scraper):
    def __init__(self):
        super().__init__()

    def get_config_key(self):
        return 'ranking'

    def init_from_config(self, config,session=None):
        ##https://log.concept2.com/rankings/2022/rower/1
        ##https://log.concept2.com/rankings/2022/bikeerg/1
        self.session = session
        self.base_url = 'https://log.concept2.com/rankings'
        self.years = config['years']
        self.ranking_pages = []
        for year in self.years:
            for machine,machine_config in config['machine'].items():
                for event in  machine_config['events']:
                    machine_type = machine_config['base_type']
                    self.ranking_pages.append(RankingPage(self.base_url,machine_type,year,event))

    def scrape(self):
        if not self.ranking_pages:
            print("there are no ranking pages to scrape, please configure properly")
            quit()

        self.ranking_pages_scrapped_count = 0
        self.data={}
        for ranking_page in self.ranking_pages:
            r = self.get_url(self.session,ranking_page.url)
            if r:
                ##find how many pages
                pages = self.page_cnt(r.text)
                ##loop through each page
                page_data = []
                for page in range(1,pages+1):
                    if page >1:
                        r = self.get_url(self.session,ranking_page.url + '&page=' + str(page))
                    single_page_result = self.scrape_page_details(r.text)
                    page_data.extend(single_page_result)
            ranking_page.set_data(page_data)
            self.data[ranking_page.get_key()] = page_data
            self.ranking_pages_count +=1

    def page_cnt(self,text):
        pages_to_scrape_cnt = 0
        tree = html.fromstring(text)
        pagination_block = tree.xpath(r'//div[@class="pagination-block"]')
        if pagination_block != []:
            pages_to_scrape_cnt = int(pagination_block[0].xpath('ul/li/a')[-2].text)
        else:
            # no pagination, only 1 page to scrape
            pages_to_scrape_cnt = 1

        return pages_to_scrape_cnt

    def scrape_page_details(self,text) -> Iterable:
        results = []

        for row in self.scrape_table_detail_by_text(text):
            if row !=[]:
                workout_link = row.xpath(r'td/a')[0].attrib['href']
                name = row.xpath(r'td/a')[0].text
                result= [c.text for c in row.xpath(r'td')]
                result[1] = name
                result.append(workout_link)
                results.append(result)
        return results




    def generate_ranking_pages(self):
        pass