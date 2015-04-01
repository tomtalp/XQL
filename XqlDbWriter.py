##########################################
# XQL
# Create an SQLite DB from the Excel file
##########################################

import sqlite3
import XqlParser
import tempfile
import datetime

class DBWriter(object):
	def __init__(self, file_path):
		self.XqlDB = XqlParser.parse_xls_to_db(file_path)
		self._db_conn = None
		self._cursor = None

	def create_db(self):
		"""
		Create the SQLite DB file

		UPDATE 30/03/2015 - function will probably be removed, since we won't be creating a DB on the disk, but writing it to RAM.

		"""

		# Update 29/03/2015 - Works on Linux, still needs Windows testing.

		temp_dir = tempfile.gettempdir()
		#self.db_path = temp_dir + self.XqlDB.name + '.db' # Waiting for XqlDB name fix 
		self.db_path = temp_dir + '/Tom' + '.db'

		db = open(db_path, 'wb')
		db.close()

		self.write_to_db() # Begin writing.


	def write_to_db(self):
		"""
		Create an SQLite DB from the XqlDB object.
		SQLite DB will be store in memory.
		"""

		self._db_conn = sqlite3.connect(":memory:") # Write to memory and not to disk to avoid dbs staying on the users system after program has exited (will happen in case of crashes i.e)
		self._cursor = self._db_conn.cursor()

		for tb in self.XqlDB.tables:
			print 'starting with '
			print tb
			self.write_tb(tb)
			print 'done with '
			print tb



	def write_tb(self, tb):
		"""
		Create & write an XqlTable object to the SQLite DB
		"""
		
		cols_for_query = ', '.join([k + ' ' + v for k, v in tb.headers.iteritems()]) # Build a string of headers and their type for the sql query

		creation_query = """
		CREATE TABLE {tb_name} (
				{cols}
			)
		""".format(tb_name = tb.name.upper(), cols = cols_for_query)

		self._cursor.execute(creation_query)


		# Insert data
		for row in tb.gen_rows:
			insertion_query = """
			INSERT INTO {tb_name}
			({cols})
			VALUES
			({vals})
			""".format(tb_name = tb.name, cols = ', '.join(row.keys()), vals = ', '.join(['?' for val in row.values()])) # ? is the Python SQLite library place holder for variables.

			self._cursor.execute(insertion_query, row.values())


		self._db_conn.commit()




	def check_data(self, tb_name):
		"""
		Test function for returning the inserted data
		"""
		return self._cursor.execute('select * from {tb_name}'.format(tb_name = tb_name)).fetchall()



#file_path = '/home/user/Desktop/big_xl.xlsx'
file_path = '/home/user/Desktop/Transactions.xls'

writer = DBWriter(file_path)

writer.write_to_db()

r = writer.check_data('sheet1')