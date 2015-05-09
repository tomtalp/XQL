from distutils.command.build_scripts import first_line_re
import xlrd
import re
import os
import random
import datetime

SQLITE3_KEYWORDS = ['ABORT', 'ACTION', 'ADD', 'AFTER', 'ALL', 'ALTER', 'ANALYZE', 'AND', 'AS', 'ASC', 'ATTACH', 'AUTOINCREMENT', 'BEFORE', 'BEGIN', 'BETWEEN', 'BY', 'CASCADE', 'CASE', 'CAST', 'CHECK', 'COLLATE', 'COLUMN', 'COMMIT', 'CONFLICT', 'CONSTRAINT', 'CREATE', 'CROSS', 'CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'DATABASE', 'DEFAULT', 'DEFERRABLE', 'DEFERRED', 'DELETE', 'DESC', 'DETACH', 'DISTINCT', 'DROP', 'EACH', 'ELSE', 'END', 'ESCAPE', 'EXCEPT', 'EXCLUSIVE', 'EXISTS', 'EXPLAIN', 'FAIL', 'FOR', 'FOREIGN', 'FROM', 'FULL', 'GLOB', 'GROUP', 'HAVING', 'IF', 'IGNORE', 'IMMEDIATE', 'IN', 'INDEX', 'INDEXED', 'INITIALLY', 'INNER', 'INSERT', 'INSTEAD', 'INTERSECT', 'INTO', 'IS', 'ISNULL', 'JOIN', 'KEY', 'LEFT', 'LIKE', 'LIMIT', 'MATCH', 'NATURAL', 'NO', 'NOT', 'NOTNULL', 'NULL', 'OF', 'OFFSET', 'ON', 'OR', 'ORDER', 'OUTER', 'PLAN', 'PRAGMA', 'PRIMARY', 'QUERY', 'RAISE', 'REFERENCES', 'REGEXP', 'REINDEX', 'RELEASE', 'RENAME', 'REPLACE', 'RESTRICT', 'RIGHT', 'ROLLBACK', 'ROW', 'SAVEPOINT', 'SELECT', 'SET', 'TABLE', 'TEMP', 'TEMPORARY', 'THEN', 'TO', 'TRANSACTION', 'TRIGGER', 'UNION', 'UNIQUE', 'UPDATE', 'USING', 'VACUUM', 'VALUES', 'VIEW', 'VIRTUAL', 'WHEN', 'WHERE']

####### Classes #######
class XqlDB(object):
    def __init__(self):
        self.name = 'MyDB'
        self.schemas = []

    def append_schema(self, xql_schema):
        """
        Check if schema name already exists, adds number suffix if it does
        """

        schema_names = [schema.name for schema in self.schemas]
        if xql_schema.name in schema_names:
            suffix = 2
            temp_schema_name = schema.name + '_1'
            while temp_schema_name in schema_names:
                temp_schema_name = schema.name + '_' + str(suffix)
                suffix += 1
            xql_schema.name = temp_schema_name

        self.schemas.append(xql_schema)

    def add_xls(self, xls_paths, rows_per_iter):
        """ parses more xls files after initial DB has been created"""
        for xls_path in xls_paths:
            if not xls_path in [xql_schema.full_path for xql_schema in self.schemas]: #Make sure the xls hasn't been parsed yet
                schema = parse_xls_to_schema(len(self.schemas), xls_path, rows_per_iter)
                self.append_schema(schema)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

class XqlSchema(object):
    def __init__(self, full_path):
        self.name = filter_name(os.path.splitext(os.path.basename(full_path))[0])
        self.full_path = full_path
        self.tables = []
        self.processed = False #To know later if it has already been created

    def add_table(self, xql_table):
        """
        if the table already exists in another scheme, add a number suffix
        """
        table_names = [table.name for table in self.tables]
        if xql_table.name in table_names:
            prefix = 2
            temp_table_name = xql_table.name + '_1'
            while temp_table_name in table_names:
                temp_table_name = '{table}_{pre}'.format(table = table.name, pre = prefix)
                prefix += 1
            xql_table.name = temp_table_name
        self.tables.append(xql_table)


    def __str__(self):
        return self.name
    def __repr__(self):
        return self.__str__()

class XqlTable(object):
    def __init__(self, name):
        self.name = filter_name(name)
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

def filter_name(name):
    """
    Validate the name to match SQL names
    Turns any non-word (letters/numbers/underscore) into an underscore
    """

    filtered_name = re.sub('\W', '_', name).upper()
    filtered_name = re.sub('[_]+', '_', filtered_name)
    filtered_name_stripped = filtered_name.strip('_')

    if not filtered_name_stripped:
        raise UnicodeError('File name, sheet name, or header names may not contain UNICODE!')

    #if the name is a sqlite3 keyword, add 'Xql_' prefix
    if filtered_name_stripped in SQLITE3_KEYWORDS:
        filtered_name_stripped = 'Xql_{name}'.format(name = filtered_name)
    return filtered_name_stripped

def parse_multiple_xls_to_db(xls_paths, rows_per_iter):
    parsed_db = XqlDB()
    for index, xls_path in enumerate(xls_paths):
        if len(xls_paths) == 1:
            schema = parse_xls_to_schema(-1, xls_path, rows_per_iter)
        else:
            schema = parse_xls_to_schema(index + 1, xls_path, rows_per_iter)
        parsed_db.append_schema(schema)
    return parsed_db

def parse_xls_to_schema(index, xls_path, rows_per_iter):

    schema = XqlSchema(xls_path)
    source_workbook = xlrd.open_workbook(xls_path)

    #Parse each sheet in the xls file
    for sheet in source_workbook.sheets():
        #print 'Now parsing {file}, sheet "{sheet_name}"'.format(file = file_name, sheet_name = sheet.name).decode('utf-8')
        table = parse_sheet_to_table(source_workbook, sheet, rows_per_iter, index)

        #Add only if table exists
        if table:
            schema.add_table(table)

    return schema

def parse_sheet_to_table(workbook, sheet, rows_per_iter, index):

    last_row = sheet.nrows - 1
    last_col = sheet.ncols - 1

    #minimum 1 rows (only header)
    if last_col >= 0:
        if index != -1:
            sheet_name = 'DB{num}_{name}'.format(num = index, name = sheet.name)
        else:
            sheet_name = sheet.name
        table = XqlTable(sheet_name)



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
                header_name = table_headers[col - first_col][0]
                value = sheet.cell_value(row, col)

                src_type = xlrd_type_to_sqlite_type(sheet.cell_type(row, col))
                target_type = table_headers[col - first_col][1]

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

    #If it's a VARCHAR, return it immediately as VARCHAR is the most generic
    if cell_type == 1:
        return cell_type

    for i in xrange(first_row + 1, last_row + 1, 5):
        count += 1
        until = min(i + 4, last_row) #to make sure the chosen row wont be bigger than the last row
        temp_type = sheet.cell_type(random.randint(i, until), col)

        #if 2 types are found, return 1 (VARCHAR)
        if cell_type != 0 and temp_type != 0 and temp_type != cell_type:
            return 1

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
            value = unicode(value)
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
        value = None #Non datetime values cannot be cast into datetime
    return value


####### End Parsing ###### end

def main():
    xls_paths = []
    xls_path = raw_input("Enter xls path:\n")
    while True:
        if os.path.isfile(xls_path):
            xls_paths.append(xls_path)
        xls_path = raw_input("Enter xls path:\n")
        if xls_path == 'end':
            break
    rows_per_iter = input("Enter number of rows you want the generator to return:\n")
    while not isinstance(rows_per_iter, int):
        rows_per_iter = input("Enter number of rows you want the generator to return:\n")
    print xls_paths
    return parse_multiple_xls_to_db(xls_paths, rows_per_iter)
