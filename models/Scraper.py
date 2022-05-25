import os,errno
from collections.abc import Iterable
import csv
import requests.exceptions
from lxml import html

class Scraper():
    def __init__(self):
        pass

    def get_config_key(self) -> str:
        pass

    def init_from_config(self, config):
        pass

    def scrape(self):
        pass

    def get_data(self) -> dict:
        if not self.data:
            print("data is scraped, or scraping is not done yet")
            return None

        return self.data

    def scrape_page_details(self,text) -> Iterable:
        pass

    def scrape_table_detail_by_text(self, text):
        tree = html.fromstring(text)
        table_tree = tree.xpath(r'//section[@class="content"]/table')
        return self.scape_table_detail_by_table_tree(table_tree)

    def scape_table_detail_by_table_tree(self, table_tree):
        if table_tree != []:
            columns = table_tree[0].xpath(r'thead/tr/th')
            headers = [column.text for column in columns]

            rows_tree = table_tree[0].xpath(r'tbody/tr')
            return rows_tree


    def get_url(self,session,url,exception_on_error = False):
        try:
            r = session.get(url)
            if r.status_code == 200:
                return r
            else:
                if exception_on_error:
                    raise ValueError("A server error code occured, status code: {}".format(r.status_code))
                else:
                    return None
        except requests.exceptions.ConnectionError:
            if exception_on_error:
                raise ValueError("cannot access url: {}".format(url))
            else:
                return None


    def write_array_result_to_file(self,results, filename):
        try:
            with open(filename, 'w',) as file:
                for result in results:
                    file.write(result+'\n')
        except:
            print('Could not open file: {0}'.format(filename))
            quit()


    def write_2d_array_result_to_file(self, results, filename):
        try:
            with open(filename, 'w', newline='') as file:
                mywriter = csv.writer(file, delimiter=',')
                mywriter.writerows(results)
        except:
            print('Could not open file: {0}'.format(filename))
            quit()

    def link(self,source,target):
        try:
            os.symlink(source, target)
        except OSError as e:
            if e.errno == errno.EEXIST:
                os.remove(target)
                os.symlink(source, target)



