from pathlib import Path
import subprocess
import sys

def result_file_name(result_file, result_view_name):
    return f'{result_view_name}-main_{result_file.with_suffix(".db").name}'

def run_mysql_convert(mysql_binary, result_file, result_view_name, output_folder):
    seperator = []
    if 'tsv' in result_file.name:
        seperator = ['-s', '\t']
    cmd = [
        mysql_binary
    ] + seperator + [
        '-t', 'Result',
        result_file,
        output_folder.joinpath(result_file_name(result_file, result_view_name))
    ]
    subprocess.run(cmd)

def main():

    mysql_binary = Path(sys.argv[1])
    output_folder = Path(sys.argv[2])
    outputs = sys.argv[3:]

    if len(outputs) % 1 == 1:
        raise Exception("Cannot have odd number of inputs after mysql_binary")

    grouped_outputs = [(outputs[2*i][1:],Path(outputs[2*i+1])) for i in range(int(len(outputs)/2))]

    for (result_view_name, result_file) in grouped_outputs:
        run_mysql_convert(mysql_binary, result_file, result_view_name, output_folder)

if __name__ == '__main__':
    main()
