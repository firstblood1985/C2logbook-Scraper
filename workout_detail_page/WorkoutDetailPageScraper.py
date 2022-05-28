from lxml import html
from collections.abc import Iterable
import os

import datetime
from models.Scraper import Scraper
from common.Utils import *
from workout_detail_page.WorkoutDetailPage import WorkoutDetailPage


class WorkoutDetailPageScraper(Scraper):
    def __init__(self):
        super().__init__()
        self.workout_details_dir = None
        self.session = None
        self.use_softlink = True
        self.workout_details_file = None
        self.workout_detail_meta_file = None
        self.max_pull = None

    def get_config_key(self) -> str:
        return 'workout_details'

    def init_from_config(self, config, session=None, cnx=None, username=''):
        self.session = session
        self.cnx = cnx
        self.workout_details_dir = config['workout_details_dir']
        self.workout_detail_meta_file = config['workout_details_meta_file']
        self.use_softlink = config['use_softlink']
        self.workout_details_file = '/'.join(
            [self.workout_details_dir, config['workout_details_file']]) + '_' + username + '_' + today()
        self.max_pull = config.get('max_pull', 10)
        try:
            os.remove(self.workout_details_file)
        except OSError as e:
            pass

        if self.use_softlink:
            self.workout_detail_meta_file = '/'.join(
                [self.workout_details_dir, self.workout_detail_meta_file]) + '_' + username
            self.link_workout_details_file = '/'.join(
                [self.workout_details_dir, config['workout_details_file']]) + '_' + username
            self.source_workout_details_file = config['workout_details_file'] + '_' + username + '_' + today()
        else:
            self.workout_detail_meta_file = '/'.join(
                [self.workout_details_dir, self.workout_detail_meta_file]) + '_' + username + '_' + today()

        ##init workout link pages from config files
        self.__generate_workout_pages_from_detail_file(self.workout_detail_meta_file)
    def check_if_processed(self,workout_detail_page):
        processed = False
        log_id = workout_detail_page.log_id
        query = """
            select count(1) as cnt from workout_summary where log_id = '{}'
        """.format(log_id)
        cursor = self.cnx.cursor()
        cursor.execute(query)
        for (cnt) in cursor:
            if cnt[0] == 1:
                print("{} is processed".format(log_id))
                processed = True
        cursor.close()

        return processed

    def scrape(self):
        if not self.workout_pages:
            print("there are no workout pages to scrape, please configure properly")
            quit()

        results = []
        count = 0
        for workout_detail_page in self.workout_pages:
            if count < self.max_pull:
                if not self.check_if_processed(workout_detail_page):
                    print("processing: " + str(workout_detail_page))
                ## check if already processed...

                    r = self.get_url(self.session, workout_detail_page.url)
                    if r:
                        result = self.scrape_summary(r.text)
                        splits = self.scrape_splits(r.text)
                        result['splits'] = splits
                        result['profile_id'] = workout_detail_page.profile_id
                        result['log_id'] = workout_detail_page.log_id
                        result['url'] = workout_detail_page.url
                    ##generate sql and write back to db
                        results.append(result)
                    count += 1

        sqls = self.generate_sqls(results)
        self.write_array_result_to_file(sqls, self.workout_details_file)
        if self.use_softlink:
            self.link(self.source_workout_details_file, self.link_workout_details_file)

    def generate_sqls(self, results) -> []:
        sql_template_full = """INSERT
INTO
workout_summary
(
create_time, update_time, workout_date_time, work_out, workout_type, weight_class, verified, ranked,
entered, meters, duration, pace, calories, average_heart_rate, average_watts, cal_per_hour,
stroke_rate, stroke_count, drag_factor, logbook_id, log_id, url)
VALUES
(CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),  '{workout_time}', '{Workout}', '{Workout Type}', '{Weight Class}', '{Verified}', '{Ranked}',
'{Entered}', {Meters}, '{Time}', '{Pace}', {Calories}, {Heart Rate}, {Average Watts}, {Calories Per Hour},
{Stroke Rate}, {Stroke Count}, {Drag Factor}, '{profile_id}', '{log_id}', '{url}'); 
"""
        split_template = """
insert
into
workout_detail(
create_time, update_time, duration, meters, pace, watts, cal_per_hour, stroke_rate, heart_rate,log_id
)values (
CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), '{}',{},'{}',{},{},{},{},'{}'
);
        """

        sqls = []
        for result in results:
            self.__complete_result_map(result)
            sqls.append(sql_template_full.format(**result))
            for split in result['splits']:
                split[1] = self.__convert_meters(split[1])
                log_id = result['log_id']
                if len(split) == 6:  ## no hear rate info
                    split.append('NULL')

                split.append(log_id)
                sqls.append(split_template.format(*split))
        return sqls

    def __convert_time(self, time):
        # March 27, 2022  12:01:00
        try:
            element = datetime.datetime.strptime(time, "%B %d, %Y  %H:%M:%S ")
        except ValueError:
            element = datetime.datetime.strptime(time, "%B %d, %Y  ")

        return element.strftime("%Y-%m-%d %H:%M:%S")

    def __convert_meters(self, meters):
        # 10,000m
        meters = meters.replace('m', '')
        meters = meters.replace(',', '')
        return int(meters)
        pass

    def __complete_result_map(self, result):
        headers = ['workout_time', 'Workout', 'Workout Type', 'Weight Class', 'Workout Type', 'Ranked', 'Verified'
                                                                                                        'Entered',
                   'Meters', 'Time', 'Pace', 'Calories', 'Heart Rate', 'Average Watts', 'Calories Per Hour',
                   'Stroke Rate', 'Stroke Count', 'Drag Factor', 'profile_id', 'log_id', 'url']

        for header in headers:
            if not result.get(header, None):
                result[header] = 'NULL'

        result['workout_time'] = self.__convert_time(result['workout_time'])
        result['Meters'] = self.__convert_meters(result['Meters'])
        return result

    # time,workout,workoutType,weightClass,verifed,ranked,entered,distance, time, pace, calories, heart rate,average watts, calories_per_hour, stroke_rate, stroke_count, drag_factor
    def scrape_summary(self, text) -> {}:
        result = {}
        tree = html.fromstring(text)
        meta_tree = tree.xpath(
            r'//section[@class="content"]/div[@class="workout"]/div[@class="col-sm-4 col-sm-pull-8 workout__details"]')
        if meta_tree != []:
            # time,workout,workoutType,weightClass,verified,ranked,entered
            result['workout_time'] = meta_tree[0].xpath("h4")[0].text
            for meta in meta_tree[0].xpath("p"):
                result[meta[0].text.strip()] = meta[1].tail.strip()

        summary_tree = tree.xpath(
            r'//section[@class="content"]/div[@class="workout"]/*/div[@class="workout__stats"]/div[@class="workout__stat"]')
        if summary_tree != []:
            # distance, time, pace, calories, heart rate
            for workout in summary_tree:
                result[workout.xpath('p')[0].text.strip()] = workout.xpath('span')[0].text.strip()

        table_tree = tree.xpath(r'//section[@class="content"]/div[@class="workout"]/*/*/*/*/*/table')
        if table_tree != []:
            # average watts, calories per hour, stroke rate, stroke count, drag factor
            # full:18, norank: 17, noheartrate: 17, norh: 16, web<15
            for stat in table_tree[1].xpath('tr'):
                result[stat.xpath('th')[0].text.strip()] = stat.xpath('td')[0].text.strip()

        return result

    def scrape_splits(self, text) -> []:
        results = []
        tree = html.fromstring(text)
        splits_table = tree.xpath(r'//section[@class="content"]/div[@class="row row-data"]/*/*/table')

        if splits_table:
            for rows in self.scape_table_detail_by_table_tree(splits_table):
                if rows != []:
                    result = [c.text for c in rows.xpath(r'td')]
                    results.append(result)
        return results

    def scrape_page_details(self, text) -> Iterable:
        results = []
        tree = html.fromstring(text)

        return results

    def __generate_workout_pages_from_detail_file(self, config_file):
        self.workout_pages = []
        fh = load_file(config_file)
        while True:
            line = fh.readline()
            if not line:
                break
            self.workout_pages.append(WorkoutDetailPage(workout_link=line))

        fh.close()
