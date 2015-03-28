################################################################################################
#
#
#           This module gets a path to an XLS(X) file and parses it.
#
#           Sheets become tables
#
################################################################################################

import xlrd, re, os


class DataBase(object):
    def __init__(self, name):
        self.name = name
        self.tables = []

    def add_table(self, table):
        self.tables.append(table)


class Table(object):
    def __init__(self, name):
        self.name = name
        self.headers = []
        self.gen_rows = None

    def add_header(self, header_name):
        #replaces all non word characters (letters, numbers and underscore) into underscores
        filtered_header_name = re.sub('\W', '_', header_name).upper()

        self.headers.append(filtered_header_name)

def parse_xls_to_db(xls_path):
    file_name = os.path.basename(xls_path)
    parsed_db = DataBase(file_name)
    source_workbook = xlrd.open_workbook(xls_path)

    #Parse each sheet in the xls file
    for sheet in source_workbook.sheets():
        table = parse_sheet_to_table(sheet)
        parsed_db.add_table(table)

    return parsed_db

def parse_sheet_to_table(sheet):
    table = Table(sheet.name)
    last_row = sheet.nrows
    last_col = sheet.ncols

    if 



