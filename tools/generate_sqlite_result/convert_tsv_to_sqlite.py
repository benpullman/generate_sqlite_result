from pathlib import Path
import sys
import sqlite3
import csv_to_sqlite

def result_file_name(result_file, result_view_name):
    return f'{result_view_name}-main_{result_file.with_suffix(".db").name}'

def rename_table(db, table_name, index_columns):
    renameTable = 'ALTER TABLE "{}" RENAME TO Result'.format(table_name)
    indexOperations = []
    for index in index_columns:
        index_name = index.replace('+','_')
        index_columns = index.replace('+',',')
        indexOperations.append('CREATE UNIQUE INDEX {} ON Result ({})'.format(index_name, index_columns))
    print(renameTable)
    connection  = sqlite3.connect(db)
    cursor      = connection.cursor()
    cursor.execute(renameTable)
    for indexOperation in indexOperations:
        cursor.execute(indexOperation)

def run_mysql_convert(result_file, result_view_name, index_columns, output_folder):
    db = output_folder.joinpath(result_file_name(result_file, result_view_name))
    # all the usual options are supported
    delimiter = ','
    if 'tsv' in result_file.name:
        delimiter = '\t'
    options = csv_to_sqlite.CsvOptions(delimiter=delimiter)
    csv_to_sqlite.write_csv([str(result_file)], str(db), options)
    rename_table(db,result_file.stem, index_columns)

def main():

    output_folder = Path(sys.argv[1])
    outputs = sys.argv[2:]

    if len(outputs) % 1 == 1:
        raise Exception("All outputs must be paired (-result_view_name result_view_file:index1,index2)")

    grouped_outputs = [(outputs[2*i][1:],Path(outputs[2*i+1].split(':')[0]),[s for s in outputs[2*i+1].split(':')[1].split(',') if s != '']) for i in range(int(len(outputs)/2))]

    for (result_view_name, result_file, index_columns) in grouped_outputs:
        run_mysql_convert(result_file, result_view_name, index_columns, output_folder)

if __name__ == '__main__':
    main()
