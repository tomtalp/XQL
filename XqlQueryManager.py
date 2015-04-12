import sqlite3
import datetime
import sqlparse

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
				raise XqlInvalidQuery("We only accept SELECT queries at the moment! Please modify your query...")

	def __exec_query(self):
		"""
		Execute a query againt the cursor

		10/04/2015 - ATM we only execute the first query. In the future we will handle several queries
		"""

		first_q = self.parsed_user_query[0]

		self.cursor.execute(first_q.to_unicode())

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
        #TODO Consider the retuan_all == True possibility
		"""
		Return results to the client.

		Once results are fetched from the cursor, try bringing the next set of results to check if there's data left.
		"""
		# The first time we fetch data, __awaiting_results is empty so we have to get new data
		if not self.__awaiting_results:
			results_for_client = self.fetch_data()
		# If we already have awaiting_results, use them	
		else:
			results_for_client = self.__awaiting_results

		self.__awaiting_results = self.fetch_data()		

		# Check if there are any results left for the next query
		if self.__awaiting_results:
			self.has_awaiting_results = True
		else:
			self.has_awaiting_results = False

		return results_for_client

	def fetch_data(self):
		"""
		Fetch & parse data from the cursor. 

		Returns a list of tuples, each tuple representing a TB row.
		Every value is casted into a string, because that's how Qt table widgets work!
		"""

		results_from_cursor = self.cursor.fetchmany(self.results_to_return)

		results_for_client = []

		for result in results_from_cursor:
			row_for_client = []
			for val in result:
				value_for_client = str(val) # First str() cast will convert numbers to strings

				# Try converting to a datetime object to check if it's a date.
				# SQLite dates are always returned in ISO-date format
				try:
					dt = datetime.datetime.strptime(value_for_client, self.date_format)			
				except ValueError:
					# This isn't a date, do nothing and stay with the original value
					pass
				else:
					# If the conversion was successful, parse with the user date_format
					#value_for_client = dt.strftime(self.date_format)
					value_for_client = dt.strftime('%d')
					
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