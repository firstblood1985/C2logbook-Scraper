import os
import getopt
import sys
import mysql.connector
import json

def load_config(config_path):
    try:
        fh = open(config_path)
        return json.load(fh)
    except:
        print('Could not open file: {0}'.format(config_path))
        quit()

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

    db_conifg = load_config(config_file)['database']
    cnx = init_db(db_conifg)

    workout_details_dir = os.getcwd()+'/workout_details/'

    for filename in os.scandir(workout_details_dir):
        if(os.path.islink(filename.path) and filename.path.find("workout_details_file_") != -1) :
            file = filename.path

            cursor = cnx.cursor()
            with open(file,'r') as f:
                lines = f.read()
                inserts = lines.split(';')
                for insert in inserts:
                    insert = insert.strip()
                    cursor.execute(insert)

            cnx.commit()
            cursor.close()

    cnx.close()
