from pathlib import Path
import subprocess
import sys
import shutil
import sqlite3
import csv_to_sqlite

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
    # all the usual options are supported
    delimiter = ','
    if 'tsv' in result_file.name:
        delimiter = '\t'
    options = csv_to_sqlite.CsvOptions(delimiter=delimiter)
    csv_to_sqlite.write_csv([str(result_file)], str(db), options)
    rename_table(db,result_file.stem)

def main():

    output_folder = Path(sys.argv[1])
    outputs = sys.argv[2:]

    if len(outputs) % 1 == 1:
        raise Exception("All outputs must be paired (-result_view_name result_view_file)")

    grouped_outputs = [(outputs[2*i][1:],Path(outputs[2*i+1])) for i in range(int(len(outputs)/2))]

    for (result_view_name, result_file) in grouped_outputs:
        run_mysql_convert(mysql_binary, result_file, result_view_name, output_folder)

if __name__ == '__main__':
    main()
