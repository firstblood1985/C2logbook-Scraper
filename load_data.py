import os

if __name__ == '__main__':
    workout_details_dir = os.getcwd()+'/workout_details/'

    for filename in os.scandir(workout_details_dir):
        if(os.path.islink(filename.path) and filename.path.find("workout_details_file_") != -1) :

            mysql_cmd = """
            mysql  -u "root" "-p12qwaszx" "c2visualizer" < "{}"
            """.format(filename.path)

            os.system(mysql_cmd)
