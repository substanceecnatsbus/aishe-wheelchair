class Logger:

    def __init__(self, log_set=None):
        if log_set == None:
            self.log_set = set()
        else:
            self.log_set = log_set

    def add_tag(self, tag):
        self.log_set.add(tag)

    def log(self, tag, data):
        if tag in self.log_set:
            print(data)
