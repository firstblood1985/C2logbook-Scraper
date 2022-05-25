import json
class TestCommon():
    def load_file(self,filename):
        try:
            fh = open(filename,'r')
            return fh
        except:
            print('Could not open file: {0}'.format(filename))
            quit()

    def string_to_dict(self,string) ->dict:
        return json.loads(string)