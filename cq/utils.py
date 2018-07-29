import datetime

def user_file_path(self, filename):
    now = datetime.datetime.now()
    return 'user_{}/{}/{}/{}/{}_{}'.format(self.owner, now.strftime('%Y'), now.strftime('%m'), now.strftime('%d'), int(now.timestamp()*1000), filename)
