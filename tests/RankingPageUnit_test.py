import unittest

from tests.TestCommon import TestCommon
from ranking_page.RankingPageScraper import RankingPageScraper


class RankingPageUnitTest(unittest.TestCase,TestCommon):

    def setUp(self) -> None:
        self.html_file = 'bikeerg_ranking_page.html'

    def test_page_cnt(self):
        scraper = RankingPageScraper()
        fh = self.load_file(self.html_file)
        pages = scraper.page_cnt(fh.read())
        self.assertEqual(9,pages,'should be 9 pages to scrape')
        fh.close()


    def test_page_detail_scrape(self):
        scraper = RankingPageScraper()
        fh = self.load_file(self.html_file)
        results = scraper.scrape_page_details(fh.read())
        self.assertEqual(50,len(results),'should be 50 rows')
        fh.close()


if __name__ == 'main':
    unittest.main()