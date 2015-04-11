################################################################################################
#
#
#           This module gets a path to an XLS(X) file and parses it.
#
#           Sheets become tables
#
################################################################################################
from distutils.command.build_scripts import first_line_re

import xlrd, re, os, random, datetime


####### Classes #######
class XqlDB(object):
    def __init__(self, name):
        self.name = name
        self.tables = []

    def add_table(self, table):
        self.tables.append(table)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class XqlTable(object):
    def __init__(self, name):
        self.name = name.upper()
        self.headers = {}
        self.gen_rows = None

    def add_header(self, header_name, header_type):
        #replaces all non word characters (letters, numbers and underscore) into underscores
        filtered_header_name = filter_name(header_name)

        if filtered_header_name in self.headers.keys():
            suffix = 1
            temp_header_name = filtered_header_name + '_1'
            while temp_header_name in self.headers.keys():
                temp_header_name = filtered_header_name + '_' + str(suffix)
                suffix += 1
            filtered_header_name = temp_header_name

        self.headers[filtered_header_name] = header_type

        return filtered_header_name

    def __repr__(self):
        return self.name

####### End Classes #######


####### Parsing #######

def filter_name(header_name):
    return re.sub('\W', '_', header_name).upper()

def parse_xls_to_db(xls_path, rows_per_iter):
    file_name = os.path.splitext(os.path.basename(xls_path))[0]
    parsed_db = XqlDB(filter_name(file_name))
    source_workbook = xlrd.open_workbook(xls_path)

    #Parse each sheet in the xls file
    for sheet in source_workbook.sheets():
        table = parse_sheet_to_table(source_workbook, sheet, rows_per_iter)

        #Add only if table exists
        if table:
            parsed_db.add_table(table)

    return parsed_db

def parse_sheet_to_table(workbook, sheet, rows_per_iter):

    last_row = sheet.nrows - 1
    last_col = sheet.ncols - 1

    #minimum 1 rows (only header)
    if last_col >= 0:

        table = XqlTable(filter_name(sheet.name))

        #If we want to find where the table actually starts (might not start at 0, 0),
        #we have to start from the last filled cell and go back until we get to the first cell
        first_row, first_col = find_first_cell(sheet, last_row, last_col)

        #Add headers
        column_nums = [] #index = column num, value = (column_name, column_type)
        for col in xrange(first_col, last_col + 1):
            header_name = sheet.cell_value(first_row, col)
            header_xlrd_type = get_column_xlrd_type(sheet, col, first_row, last_row)
            header_sqlite_type = xlrd_type_to_sqlite_type(header_xlrd_type)
            filtered_header_name = table.add_header(header_name, header_sqlite_type)
            column_nums.append((filtered_header_name, header_sqlite_type))

        table.gen_rows = generate_sheet_rows(workbook, sheet, first_row, last_row, first_col, last_col, column_nums, rows_per_iter)
        return table

    return False

def find_first_cell(sheet, last_row, last_col):
    """ Returns the first row and column of the table in the sheet """
    first_row = find_first_row(sheet, last_row, last_col)

    #Here we give the first row because That is the only one that must contain a value in its first column
    #because it's a header

    first_col = find_first_col(sheet, first_row, last_col)
    return (first_row, first_col)

def find_first_row(sheet, last_row, last_col):
    """ scans the whole last column from the beginning.
    first cell with a value is the table's first row (headers)
    """
    for row in xrange(last_row):
        if sheet.cell_value(row, last_col):
            return row

def find_first_col(sheet, first_row, last_col):
    """ scans the whole first row from the beginning.
    first cell with a value is the table's first column
    """
    for col in xrange(last_col):
        if sheet.cell_value(first_row, col):
            return col


def generate_sheet_rows(workbook, sheet, first_row, last_row, first_col, last_col, table_headers, rows_per_iter = 5):
    """

    returns a generator and yields a dictionary having the cell_value as value and header_name as key

    """

    #Start from rows and not headers
    row = first_row + 1

    while row <= last_row:
        rows_block = []
        origin_row = row

        #yields a list wirh rows_per_iter rows
        while row < origin_row + rows_per_iter and row <= last_row:
            row_values = {}
            for col in xrange(first_col, last_col + 1):
                header_name = table_headers[col][0]
                value = sheet.cell_value(row, col)

                src_type = xlrd_type_to_sqlite_type(sheet.cell_type(row, col))
                target_type = table_headers[col][1]

                if src_type == target_type == 'DATETIME':
                    year, month, date, hour, minute, second = xlrd.xldate_as_tuple(value, workbook.datemode)
                    value = datetime.datetime(year, month, date, hour, minute, second)
                if src_type != target_type:
                    value = convert_cell_type(value, src_type, target_type, workbook.datemode)

                row_values[header_name] = value
            rows_block.append(row_values)
            row += 1

        yield rows_block


def xlrd_type_to_sqlite_type(code):
    """
    gets the xlrd code from sheet.cell_value, and returns its corresponding Sqlite type
    """

    return {
        1: "VARCHAR", # 1 is TEXT
        2: "FLOAT", #2 is Number (could be float or int so we choose float to be sure
        3: "DATETIME", #3 is date
        4: "BOOLEAN", #4 is boolean
        0: "VARCHAR", 5: "VARCHAR", 6: "VARCHAR" #empty unicode string
    } [code]

def get_column_xlrd_type(sheet, col, first_row, last_row):
    """
    finds the columns type by scanning 20% of cells. if it finds more than 1 type, its varchar
    """

    count = 1

    until = until = min(first_row + 5, last_row)

    cell_type = sheet.cell_type(random.randint(first_row + 1, until), col)
    print "CELL TYPE: {CELL}".format(CELL = cell_type)
    for i in xrange(first_row + 5, last_row + 1, 5):
        count += 1
        until = min(i + 4, last_row)
        temp_type = sheet.cell_type(random.randint(i, until), col)
        print "CELL TYPE: {CELL}".format(CELL = temp_type)
        #if 2 types are found, return 1 (VARCHAR)
        #print cell_type, temp_type
        if cell_type != 0 and temp_type != 0 and temp_type != cell_type:
            print "RETURNED {CELL} after {COUNT} loops".format(CELL = cell_type, COUNT = count)
            return cell_type

        elif temp_type != 0:
            cell_type = temp_type
    else:
        #No 2 cells have different values
        return cell_type

def convert_cell_type(value, src_type, target_type, datemode):
    """

    gets sqlite source and target type, and converts the value if necessary
    This func is only called when src_type and target_type are different

    Dates that must be converted to string are converted into the following format: %d-%m-%Y %H:%M

    """
    if target_type == 'VARCHAR':
        if src_type == 'DATETIME':
            year, month, date, hour, minute, second = xlrd.xldate_as_tuple(value, datemode)
            python_date = datetime.datetime(year, month, date, hour, minute, second)
            value = python_date.strftime('%d-%m-%Y %H:%M')
        elif src_type in ('FLOAT', 'BOOLEAN'):
            value = str(value)
    elif target_type == 'FLOAT':
        if src_type == 'BOOLEAN':
            value = float(True)
        elif src_type == 'VARCHAR':
            value = 0 # default float
        elif src_type == 'DATETIME': # Dates are stored as float numbers
            pass
    elif target_type == 'BOOLEAN':
        value = bool(value)
    elif target_type == 'DATETIME':
        value = None
    return value


####### End Parsing ###### end

def main():
    xls_path = raw_input("Enter xls path:\n")
    while not (os.path.isfile(xls_path) and os.path.splitext(xls_path)[1] in ('.xls', '.xlsx')):
        xls_path = raw_input("Enter xls path:\n")
    rows_per_iter = input("Enter number of rows you want the generator to return:\n")
    while not isinstance(rows_per_iter, int):
        rows_per_iter = input("Enter number of rows you want the generator to return:\n")
    return parse_xls_to_db(xls_path, rows_per_iter)
