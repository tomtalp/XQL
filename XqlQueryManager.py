import sqlite3
import datetime
import sqlparse

class XqlQuery(object):
	def __init__(self, cursor, query, results_to_return = 20):
		self.cursor = cursor
		self.query = query
		self.results_to_return = results_to_return
		self.parsed_user_query = sqlparse.parse(self.query)
		self.rows_returned = 0 # How many results have been returned to the user so far
		self.headers = None

		####### TODO #######
		self.has_more = False 
		self.max_results = 0 # How many results can this query possibly produce
		####################

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
		pass
		#TODO

	def get_results(self):
		"""
		Returns a list of tuples, each tuple representing a TB row.

		Every value is casted into a string, because that's how Qt table widgets work!
		"""

		results = []

		results_from_cursor = cursor.fetchmany(self.results_to_return)

		for result in results_from_cursor:
			new_row = []
			for val in result:
				if isinstance(val, int) or isinstance(val, float):
					new_row.append(str(val))
				elif isinstance(val, datetime.datetime):
					new_row.append('%d/%m/%Y %H:%M:%S')
				else:
					new_row.append(str(val))
			results.append(new_row)

		self.rows_returnd += self.results_to_return
		self.__check_if_more()
		return results



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