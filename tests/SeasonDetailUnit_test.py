import unittest

from tests.TestCommon import TestCommon
from season_page.SeasonDetailScraper import SeasonDetailScraper


class SeasonDetailTestCase(unittest.TestCase,TestCommon):
    def setUp(self) -> None:
        self.html_file = 'season_details_page.html'

    def test_season_detail_scrape(self):
        scraper = SeasonDetailScraper()
        fh = self.load_file(self.html_file)
        results = scraper.scrape_page_details(fh.read())
        self.assertEqual(624,len(results),'should be 621 rows')
        fh.close()
        workout_links = scraper.get_workout_links(results)
        scraper.write_array_result_to_file(workout_links,"workout_details/workout_details_meta_file_20220425")




if __name__ == '__main__':
    unittest.main()
