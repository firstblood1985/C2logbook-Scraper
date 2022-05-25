import getopt
import os
import requests
import json
import sys
from lxml import etree, html
import mysql.connector
from season_page.SeasonDetailScraper import SeasonDetailScraper
from workout_detail_page.WorkoutDetailPageScraper import WorkoutDetailPageScraper


class MainScraper():
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.s = requests.session();
        self.url_login = self.config['url_login']
        self.url_log = self.config['url_log']
        db_config = self.config['database']
        self.cnx = init_db(db_config)
        self.c2users = self.get_username_password(self.cnx)

    def scrape(self):
        ##init scrapers
        self.scrapers = [SeasonDetailScraper(), WorkoutDetailPageScraper()]
        for (username, password) in self.c2users:
            session = requests.session()
            session = C2_login(session, self.url_login, username, password, self.url_log)
            for scraper in self.scrapers:
                scraper.init_from_config(self.config['to_scrape'][scraper.get_config_key()], session, self.cnx,
                                         username)
                scraper.scrape()

    def load_config(self, config_path):
        try:
            fh = open(config_path)
            return json.load(fh)
        except:
            print('Could not open file: {0}'.format(config_path))
            quit()

    def finish(self):
        if self.cnx:
            self.cnx.close()

    def get_username_password(self, cnx) -> []:
        results = []
        cursor = cnx.cursor()
        query = """
                SELECT username, password FROM c2user
                """
        cursor.execute(query)
        for (username, password) in cursor:
            print("{}, {} was found ".format(username, password))
            results.append((username, password))

        cursor.close()
        return results


def C2_login(session, url_login, username, password, url_login_success):
    login = session.get(url_login)
    login_tree = html.fromstring(login.text)
    hidden_inputs = login_tree.xpath(r'//form//input[@type="hidden"]')
    form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}  # get csrf token
    form['username'] = username
    form['password'] = password
    response = session.post(url_login, data=form)
    if response.url != url_login_success:
        sys.exit('unable to login, quitting')
    else:
        print('Logged in')

    return session


def init_db(config):
    if config:
        cnx = mysql.connector.connect(**config)
        return cnx


if __name__ == '__main__':
    config_file = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:", ["config="])
    except getopt.GetoptError:
        print('MyC2Scraper.py -c <config_file>')
        quit()
    for opt, arg in opts:
        if opt == '-h':
            print('MyC2Scraper.py -c <config_file>')
            quit(0)
        elif opt in ('-c', '--config'):
            config_file = arg

    if config_file == '':
        config_file = os.getcwd() + '/MyC2Config.json'

    print('config file: {}'.format(config_file))
    scraper = MainScraper(config_file)
    scraper.scrape()
    scraper.finish()
