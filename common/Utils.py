from datetime import date
def today():
    today = date.today()
    return today.strftime('%Y%m%d')

def load_file(filename):
    try:
        fh = open(filename,'r')
        return fh
    except:
        print('Could not open file: {0}'.format(filename))
        quit()
