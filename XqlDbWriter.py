##########################################
# XQL
# Create an SQLite DB from the Excel file
##########################################

import sys
import sqlite3
import XqlParser

class DBWriter(object):
	def __init__(self, file_path):
		self.XQL_db_object = XqlParser.parse_xls_to_db(file_path)
		self.db_location = None

	def create_db(self):
		"""
		Create the SQLite DB file
		"""
		pass
		#Modify self.db_location

		#TODO - Decide whether we write in cwd or /tmp/

	def write_to_db(self):
		db_conn = sqlite3.connect(self.db_location)
