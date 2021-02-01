import re


class Annotator:
    def annotator(self, code):
        file_data = code
        length = len(file_data)
        for index in range(length):
            s = re.compile(r'//.*')
            file_data[index] = re.sub(s, '', file_data[index])
        file_data = ''.join(file_data)
        s = re.compile(r'/\*.*?\*/', re.S)
        file_data = re.sub(s, '', file_data)
        return file_data


annotator = Annotator()


del Annotator
