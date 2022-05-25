import unittest

from tests.TestCommon import TestCommon
from workout_detail_page.WorkoutDetailPage import WorkoutDetailPage
from workout_detail_page.WorkoutDetailPageScraper import WorkoutDetailPageScraper
import time
import datetime
import mysql.connector


class WorkoutDetailPageScraperUnitTest(unittest.TestCase, TestCommon):
    def setUp(self) -> None:
        self.workout_detail_file = 'workout_details/workout_details_meta_file'
        self.html_file = 'single_workout_details.html'
        config_string = """
        {
        "workout_details": { 
            "workout_details_dir": "workout_details", 
            "workout_details_meta_file": "workout_details_meta_file", 
            "workout_details_file": "workout_details_file",
            "use_softlink": true
            }
        }
        """
        config = self.string_to_dict(config_string)
        self.scraper = WorkoutDetailPageScraper()
        self.scraper.init_from_config(config['workout_details'])
        self.workout_detail_page = WorkoutDetailPage(workout_link="https://log.concept2.com/profile/1043029/log/63324246");

    def test_init_from_config(self):

        self.assertEqual(2, len(self.scraper.workout_pages), 'should have 2 workout detail pages')

    def test_scrape_summary(self):
        fh = self.load_file(self.html_file)
        results = []
        result = self.scraper.scrape_summary(fh.read())
        result['profile_id'] = self.workout_detail_page.profile_id
        result['log_id'] = self.workout_detail_page.log_id
        result['url'] = self.workout_detail_page.url
        results.append(result)
        self.assertEqual(20,len(result),'should be 20 workout stats')
        fh.close()
        sqls = self.scraper.generate_sqls(results)
        self.scraper.write_array_result_to_file(sqls,self.scraper.workout_details_file)
        self.scraper.link(self.scraper.source_workout_details_file,self.scraper.link_workout_details_file)

    def test_scrape_splits(self):
        fh = self.load_file(self.html_file)
        result = self.scraper.scrape_splits(fh.read())
        print(result)
        self.assertEqual(5,len(result),'should be 5 splits')
        fh.close()

    def test_timestamp(self):
        time = 'March 27, 2022  12:01:00 '
        element = datetime.datetime.strptime(time, "%B %d, %Y  %H:%M:%S ")

        print(element.year)
        print(element.timestamp())


    def test_db_conn(self):
        config_string = """
        {
        "database": {
            "user": "root",
            "password": "12qwaszx",
            "host": "localhost",
            "database": "c2visualizer"
                    }
        }
        """
        config =self.string_to_dict(config_string)['database']
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()


        username = "firstblood1985"
        query = """
        SELECT username, password FROM c2user
        where username = "{}"
        """.format(username)

        cursor.execute(query)

        for (username, password) in cursor:
            print("{}, {} was found ".format(username, password))

        cursor.close()
        cnx.close()