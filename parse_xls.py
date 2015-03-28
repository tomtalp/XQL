################################################################################################
#
#
#           This module gets a path to an XLS(X) file and parses it.
#
#           Sheets become tables
#
################################################################################################
from distutils.command.build_scripts import first_line_re

import xlrd, re, os

class DataBase(object):
    def __init__(self, name):
        self.name = name
        self.tables = []

    def add_table(self, table):
        self.tables.append(table)

    def __repr__(self):
        return self.__str__()


class Table(object):
    def __init__(self, name):
        self.name = name
        self.headers = []
        self.gen_rows = None

    def add_header(self, header_name):
        #replaces all non word characters (letters, numbers and underscore) into underscores
        filtered_header_name = filter_header(header_name)

        self.headers.append(filtered_header_name)

        return filtered_header_name

    def __repr__(self):
        return self.name

def filter_header(header_name):
    return re.sub('\W', '_', header_name).upper()

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
    last_row = sheet.nrows - 1
    last_col = sheet.ncols - 1

    #If we want to find where the table actually starts (might not start at 0, 0),
    #we have to start from the last filled cell and go back until we get to the first cell
    first_row, first_col = find_first_cell(sheet, last_row, last_col)

    #Add headers
    for col in xrange(first_col, last_col + 1):
        table.add_header(sheet.cell_value(first_row, col))

    table.gen_rows = generate_sheet_rows(sheet, first_row, last_row, first_col, last_col)

    return table

def find_first_cell(sheet, last_row, last_col):
    """ Returns the first row and column of the table in the sheet """
    first_row = find_first_row(sheet, last_row, last_col)
    first_col = find_first_col(sheet, last_row, last_col)
    return (first_row, first_col)

def find_first_row(sheet, last_row, last_col):
    """ recursive func to find the first col """
    if last_row == 0:
        return 0
    elif not sheet.cell_value(last_row, last_col):
        return last_row + 1
    return find_first_row(sheet, last_row - 1, last_col)

def find_first_col(sheet, last_row, last_col):
    """ recursive func to find the first column """
    if last_col == 0:
        return 0
    elif not sheet.cell_value(last_row, last_col):
        return last_col + 1
    return find_first_row(sheet, last_row, last_col - 1)


def generate_sheet_rows(sheet, first_row, last_row, first_col, last_col):
    """

    returns a generator and yields every time a dictionary having the cell_value as value and header_name as key

    """

    #Start from rows and not headers
    row = first_row + 1

    while row < last_row:
        row_values = {}
        for col in xrange(first_col, last_col + 1):
            header_name = filter_header(sheet.cell_value(first_row, col))
            value = sheet.cell_value(row, col)
            row_values[header_name] = value
        yield row_values
        row +=1

