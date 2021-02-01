import getopt
import re
import sys

from annotator import annotator
from lexical_analyzer import lexical_analyzer


def main(argv):
    input_file = ''
    output_file = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["in=", "out="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--in"):
            input_file = arg
        elif opt in ("-o", "--out"):
            output_file = arg
    print('输入的文件为：', input_file)
    with open(input_file) as f:
        file_data = f.readlines()
        code = annotator.annotator(file_data)
        lexical_analyzer.analyzer(code)
        print(file_data)
    print('输出的文件为：', output_file)


if __name__ == "__main__":
    main(sys.argv[1:])
