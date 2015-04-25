##########################################
# XQL
# Create an SQLite DB from the Excel file
##########################################

import sqlite3
import XqlParser

class DBWriter(object):
    def __init__(self, file_paths, bulk_amount = 5):
        self.bulk_amount = bulk_amount
        self.XqlDB = XqlParser.parse_multiple_xls_to_db(file_paths, self.bulk_amount)

        # Write to memory and not to disk to avoid dbs staying on the users system after program has exited (will happen in case of crashes i.e)
        self.db_conn = sqlite3.connect(":memory:", check_same_thread = False)
        self.cursor = self.db_conn.cursor()

    def write_to_db(self):
        """
        Write an XqlDB to SQLite
        """
        for schema in self.XqlDB.schemas:
            for tb in schema.tables:
                print 'starting with '
                print tb
                self.create_tb(tb)
                print 'done with '
                print tb

    def create_tb(self, tb):
        """
        Create & write an XqlTable object to the SQLite DB
        """

        cols_for_query = ', '.join([k + ' ' + v for k, v in tb.headers.iteritems()]) # Build a string of headers and their type for the sql query

        creation_query = """
        CREATE TABLE {tb_name} (
                {cols}
            )
        """.format(tb_name = tb.name.upper(), cols = cols_for_query)
        print creation_query
        self.cursor.execute(creation_query)

        insertion_query = """
        INSERT INTO {tb_name}
        ({cols})
        VALUES
        ({vals})
        """.format(tb_name = tb.name, cols = ', '.join(tb.headers.keys()), vals = ', '.join(['?' for val in range(len(tb.headers))])) # ? is the Python SQLite library place holder for variables.

        # Insert data
        for gen_obj in tb.gen_rows:
            self.cursor.executemany(insertion_query, map(lambda x: x.values(), gen_obj))


        self.db_conn.commit()

# file_path = '/home/user/Desktop/Transactions.xls'
# file_path = '/home/user/Desktop/TestExcel.xls'
#file_path = '/home/user/Desktop/test.xlsx'
file_path = '/home/user/Desktop/busfin.xls'




