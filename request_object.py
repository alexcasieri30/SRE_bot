class RequestJQL:
    def __init__(self):
        self.name = None
        self.res_start = "2020/04/15"
        self.res_end = None
        self.max_results = 10
        self.all = False

    def set_start(self, start_time):
        self.res_start = start_time
        return

    def set_end(self, end_time):
        self.res_end = end_time
        return

    def set_max_results(self, num):
        self.max_results = num
        return

    def set_assignee(self, name):
        self.name = name
        return

    def set_all(self, all):
        self.all = all
        return

    def get_start(self):
        return self.res_start

    def get_end(self):
        return self.res_end

    def get_max_results(self):
        return self.max_results

    def get_assignee(self):
        return self.name

    def get_all(self):
        return self.all