import datetime
import sqlparse
import sqlite3

class XqlQuery(object):
	def __init__(self, cursor, query, results_to_return = 20, date_format = '%d/%m/%Y %H:%M:%S'):
		self.cursor = cursor
		self.query = query
		self.results_to_return = results_to_return
		self.date_format = date_format
		self.parsed_user_query = sqlparse.parse(self.query)
		self.headers = None

		self.has_awaiting_results = False 
		self.__awaiting_results = None

		self.__exec()

	def __exec(self):
		"""
		Main function for executing the query operations
		"""

		self.__validate_query()
		self.__exec_query()
		self.__get_headers()

	def __validate_query(self):
		"""
		Check whether a query is valid, both syntactically and legally (security wise).

		Currently we don't allow anything that isn't a SELECT query, and only one query at a time.
		"""

		for query in self.parsed_user_query:
			if query.get_type() != 'SELECT':
				raise XqlInvalidQuery("We only accept SELECT queries! Please modify your query...")

	def __exec_query(self):
		"""
		Execute a query againt the cursor

		10/04/2015 - ATM we only execute the first query. In the future we will handle several queries
		"""

		first_q = self.parsed_user_query[0]

		try:
			self.cursor.execute(first_q.to_unicode())
		except sqlite3.OperationalError, sqlite_error:
			error_msg = "Error! " + sqlite_error.message
			raise XqlInvalidQuery(error_msg)

	def __get_headers(self):
		"""
		Parse cursor.description for headers
		"""
		self.headers = [obj[0] for obj in self.cursor.description]

	def __check_if_more(self):
		"""
		Checking whether there are any results left in the cursor, and update class state accordingly.
		Allows UI to know if user can fetch more rows
		"""
		#TODO
		pass

	def get_results(self, return_all = False):
		"""
		Return results to the client.

		Once results are fetched from the cursor, try bringing the next set of results to check if there's data left.
		"""

		if return_all:
			# Get all the rows left in the cursor + awaiting results from previous times
			# Order matters because we want to bring the previous results before the newly fetched data.
			results_for_client = self.__awaiting_results + self.fetch_data(return_all) 
			self.__awaiting_results = None
			self.has_awaiting_results = False
		else:
			# The first time we fetch data, __awaiting_results is empty so we have to get new data
			if not self.__awaiting_results:
				results_for_client = self.fetch_data(return_all)
			# If we already have awaiting_results, use them	
			else:
				results_for_client = self.__awaiting_results

			self.__awaiting_results = self.fetch_data(return_all)		

			# Check if there are any results left for the next query
			if self.__awaiting_results:
				self.has_awaiting_results = True
			else:
				self.has_awaiting_results = False

		return results_for_client

	def fetch_data(self, fetch_all = False):
		"""
		Fetch & parse data from the cursor. 

		Returns a list of tuples, each tuple representing a TB row.
		Every value is casted into a string, because that's how Qt table widgets work!
		"""

		if fetch_all:
			results_from_cursor = self.cursor.fetchall()
		else:
			results_from_cursor = self.cursor.fetchmany(self.results_to_return)

		results_for_client = []

		for result in results_from_cursor:
			row_for_client = []
			for val in result:

				value_for_client = val

				# Convert floats that are a whole number to integers.					
				if isinstance(value_for_client, float) and value_for_client.is_integer():
					value_for_client = int(value_for_client) 

				try:
					value_for_client = str(value_for_client) # Convert numbers or anything else to strings
				except UnicodeEncodeError:
					value_for_client = unicode(value_for_client)

				# Try converting to a datetime object to check if it's a date.
				# SQLite dates are always returned in ISO-date format
				try:
					dt = datetime.datetime.strptime(value_for_client, '%Y-%m-%d %H:%M:%S')

				except ValueError:
					# This isn't a date, do nothing and stay with the original value
					pass
				else:
					# If the conversion was successful, parse with the user date_format
					value_for_client = dt.strftime(self.date_format)
					
				if value_for_client is None:
					value_for_client = ""
							
				row_for_client.append(value_for_client)
			
			results_for_client.append(row_for_client)

		return results_for_client




class XqlInvalidQuery(Exception):
	"""
	Invalid query exception - Create, Update, Delete etc. queries are illegal.

	10/04/2015 - Only SELECT queries are allowed atm. Once we enable additional queries, we still won't allow all instructions.
	"""
	def __init__(self, msg = ''):
		self.msg = msg

	def __str__(self):
		return self.msg


#q1 = "SELECT * FROM SHEET1"