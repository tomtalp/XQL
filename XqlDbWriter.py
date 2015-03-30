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
		Main writing function - write all the tables to the DB
		"""
		self._db_conn = sqlite3.connect(":memory:")
		self._cursor = self._db_conn.cursor()

		for tb in self.XqlDB.tables:
			self.write_tb(tb)



	def write_tb(self, tb):
		"""
		Create & write an XqlTable object to the Sqlite DB
		"""
		
		cols_for_query = ', '.join([k + ' ' + v for k, v in tb.headers.iteritems()]) # Build a string of headers and their type for the sql query

		creation_query = """
		CREATE TABLE {tb_name} (
				{cols}
			)
		""".format(tb_name = tb.name.upper(), cols = cols_for_query)

		self._cursor.execute(creation_query)
		self._db_conn.commit()


	def get_creation_query(self, XqlTable):
		pass




file_path = '/home/user/Desktop/big_xl.xlsx'

writer = DBWriter(file_path)