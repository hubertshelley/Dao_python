import getopt
import re
import sys


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
        length = len(file_data)
        for index in range(length):
            s = re.compile(r'//.*')
            file_data[index] = re.sub(s, '', file_data[index])
        file_data = ''.join(file_data)
        s = re.compile(r'/\*.*?\*/', re.S)
        file_data = re.sub(s, '', file_data)
        print(file_data)
    print('输出的文件为：', output_file)


if __name__ == "__main__":
    main(sys.argv[1:])
