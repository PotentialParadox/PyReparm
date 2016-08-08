import re


class Header:
    def __init__(self, from_header_string=None):
        if from_header_string:
            self.command = self.find_command(from_header_string)
            self.title = self.find_title(from_header_string)

    def find_command(self, header_string):
        p_command = re.compile("^(.+\n)+")
        m = re.search(p_command, header_string)
        return m.group(0)

    def find_title(self, header_string):
        p_title = re.compile("^(.+\n)+\n(.+\n)")
        m = re.search(p_title, header_string)
        return m.group(2)

    def str(self):
        return self.command + "\n" + self.title + "\n"
