from pathlib import Path
import subprocess
import sys
import shutil
import sqlite3

def result_file_name(result_file, result_view_name):
    return f'{result_view_name}-main_{result_file.with_suffix(".db").name}'

def rename_table(db, table_name):
    renameTable = 'ALTER TABLE "{}" RENAME TO Result'.format(table_name)
    print(renameTable)
    connection  = sqlite3.connect(db)
    cursor      = connection.cursor()
    cursor.execute(renameTable)

def run_mysql_convert(mysql_binary, result_file, result_view_name, output_folder):
    db = output_folder.joinpath(result_file_name(result_file, result_view_name))
    seperator = []
    if 'tsv' in result_file.name:
        seperator = ['--delimiter', '\t']
    cmd = [
        mysql_binary
    ] + seperator + [
        '--file', result_file,
        '--output', db
    ]
    print(cmd)
    p = subprocess.run(cmd)
    rename_table(db,result_file.stem)

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
