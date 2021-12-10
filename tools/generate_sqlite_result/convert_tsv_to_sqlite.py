from pathlib import Path
import argparse
import configparser
import csv_to_sqlite
import os
import sqlite3
import sys
import time

# recognized SQLite column data types
SQLITE_TYPES = ["TEXT", "INTEGER", "REAL", "NUMERIC", "BLOB"]

# lambda to get current time in milliseconds
current_time_ms = lambda: int(round(time.time() * 1000))

def result_file_name(result_file, result_view_name):
    return f'{result_view_name}_{result_file.with_suffix(".db").name}'

# convert elapsed time in milliseconds to human-readable string format
def format_ms(elapsed):
    message = ""
    days = elapsed // 86400000
    if days != 0:
        message += "{:,}".format(days) + " day"
        if days != 1:
            message += "s"
        message += ", "
    hours = (elapsed % 86400000) // 3600000
    if hours != 0:
        message += str(hours) + " hour"
        if hours != 1:
            message += "s"
        message += ", "
    minutes = (elapsed % 3600000) // 60000
    if minutes != 0:
        message += str(minutes) + " minute"
        if minutes != 1:
            message += "s"
        message += ", "
    seconds = (elapsed % 60000) // 1000
    milliseconds = elapsed % 1000
    message += str(seconds) + ":" + str(milliseconds) + " second"
    if seconds != 1 or milliseconds != 0:
        message += "s"
    return message

def create_indexes(db, index_columns):
    indexOperations = []
    if index_columns is not None:
        for index in index_columns:
            index_name = index.replace(' ','_').replace('+','_')
            index_columns = ','.join(['"{}"'.format(i) for i in index.split('+') if i != ''])
            indexOperations.append('CREATE INDEX index_{} ON Result ({})'.format(index_name, index_columns))
    connection  = sqlite3.connect(db)
    cursor      = connection.cursor()
    for indexOperation in indexOperations:
        print(indexOperation)
        cursor.execute(indexOperation)

def run_sqlite_convert(result_file, result_view_name, column_types, index_columns, output_folder):
    print("Input TSV result file  = [" + str(result_file.resolve()) + "]")
    db = output_folder.joinpath(result_file_name(result_file, result_view_name))
    print("Output SQLite database file = [" + str(db.resolve()) + "]")
    # all the usual options are supported
    delimiter = '\t'
    if 'csv' in result_file.name:
        delimiter = ','
    options = None
    if column_types is not None:
        options = csv_to_sqlite.CsvOptions(delimiter=delimiter, typing_style='manual', column_types=column_types, column_select_func=lambda x:x in column_types.keys())
    else:
        options = csv_to_sqlite.CsvOptions(delimiter=delimiter)
    print("Converting...")
    sys.stdout.flush()
    start = current_time_ms()
    csv_to_sqlite.write_csv([str(result_file)], str(db), options)
    end = current_time_ms()
    print("  Completed in " + format_ms(end - start))
    print("Post-processing database...")
    sys.stdout.flush()
    start = end
    create_indexes(db, index_columns)
    end = current_time_ms()
    print("  Completed in " + format_ms(end - start))
    sys.stdout.flush()

def get_parameters(parameter_file):
    if not os.path.isfile(parameter_file):
        return None, None, None, None
    # parse parameter file
    configuration = configparser.ConfigParser(allow_no_value=True, delimiters=('='), comment_prefixes=None)
    configuration.optionxform = str
    configuration.read(parameter_file)
    # extract relevant parameters
    result_view_name = None
    input_tsv_file = None
    column_types = None
    indexes = None
    # basic database parameters
    try:
        database_parameters = dict(configuration.items("SQLite Database"))
        try:
            result_view_name = database_parameters["view"]
            input_tsv_file = database_parameters["file"]
        except KeyError:
            print("ERROR: Parameter file [" + parameter_file + "] contains an invalid [SQLite Database] section - both \"view\" and \"file\" parameters must be provided.")
            sys.exit(1)
    except configparser.NoSectionError:
        result_view_name = None
        input_tsv_file = None
    # columns
    try:
        column_parameters = dict(configuration.items("Columns"))
        if len(column_parameters) > 0:
            column_types = {}
            for column, type in column_parameters.items():
                if type.upper() not in SQLITE_TYPES:
                    print("WARNING: Configured column type [" + type + "] for column [" + column + "] is not a recognized SQLite data type - setting this column's type to TEXT instead.")
                    type = "TEXT"
                column_types[column] = type.upper()
            if len(column_types) < 1:
                column_types = None
    except configparser.NoSectionError:
        column_types = None
    # indexes
    try:
        index_parameters = dict(configuration.items("Indexes"))
        if len(index_parameters) > 0:
            if column_types is None:
                print("WARNING: Parameter file [" + parameter_file + "] contains an [Indexes] section without a [Columns] section - ignoring.")
            else:
                column_names = column_types.keys()
                indexes = []
                for index in index_parameters.keys():
                    if index not in indexes:
                        columns = index.split("+")
                        columns_valid = True
                        for column in columns:
                            if column not in column_names:
                                print("WARNING: Declared index [" + index + "] refers to unknown column [" + column + "] - ignoring.")
                                columns_valid = False
                                break
                        if columns_valid:
                            indexes.append(index)
                if len(indexes) < 1:
                    indexes = None
    except configparser.NoSectionError:
        indexes = None
    return result_view_name, input_tsv_file, column_types, indexes

def get_db_config(db_config):
    if db_config is None:
        return None, None, None
    # parse argument db config string value
    tokens = db_config.split(":")
    if len(tokens) > 3:
        print("ERROR: Database configuration parameter argument [" + db_config + "] is invalid - it should consist of 2-3 tokens delimited by colon characters (\":\").")
        sys.exit(1)
    # extract relevant parameters
    result_view_name = tokens[0]
    input_tsv_file = tokens[1]
    # indexes
    indexes = None
    if len(tokens) == 3:
        indexes = tokens[2].split(",")
    return result_view_name, input_tsv_file, indexes

def main():
    # get command line arguments
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-d", "--database", help="<result_view_name>:<result_view_file>[:<index1>,<index2>,...]")
    argument_parser.add_argument("-p", "--parameter_file", help="Text properties file (key=value per line) for configuring the SQLite database build.")
    argument_parser.add_argument("-o", "--output_folder", required=True, help="Output directory for generated SQLite database files.")
    arguments = argument_parser.parse_args(sys.argv[1:])
    # get output folder
    output_folder = Path(arguments.output_folder)
    # get database build parameters from configuration file
    result_view_name, input_tsv_file, column_types, indexes = get_parameters(arguments.parameter_file)
    # if no parameter file was provided, or if view and/or result file were not provided
    # in the parameter file, check --database command line argument
    if result_view_name is None or input_tsv_file is None:
        result_view_name, input_tsv_file, cli_indexes = get_db_config(arguments.database)
        if cli_indexes is not None:
            if indexes is not None:
                print("WARNING: Index specifications found in both parameters file [" + arguments.parameter_file + "] and -d/--database parameter argument [" + arguments.database + "] - ignoring command line indexes and using those specified in the parameter file.")
            else:
                indexes = cli_indexes
    # validate required parameters
    if result_view_name is None or input_tsv_file is None:
        print("ERROR: You must provide either a valid parameter file (-p/--parameter_file) or command-line database configuration (-d/--database).")
        sys.exit(1)
    elif not os.path.isfile(input_tsv_file):
        print("ERROR: Argument TSV result file [" + input_tsv_file + "] is not a valid readable file.")
        sys.exit(1)
    # convert result file to SQLite database
    run_sqlite_convert(Path(input_tsv_file), result_view_name, column_types, indexes, output_folder)

if __name__ == '__main__':
    main()
