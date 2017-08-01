import anvil.server


class AppTables:
	cache = None

	def __getattr__(self, name):
		if AppTables.cache is None:
			AppTables.cache = anvil.server.call("anvil.private.tables.get_app_tables")

		tbl = AppTables.cache.get(name)
		if tbl is not None:
			return tbl

		raise AttributeError("No such app table: '%s'" % name)

	def __setattr__(self, name, val):
		raise Exception("app_tables is read-only")


app_tables = AppTables()


#!defClass(tables,TableError)!:
class TableError(anvil.server.AnvilWrappedError):
	pass


#!defClass(tables,TransactionConflict,tables.TableError)!:
class TransactionConflict(TableError):
	pass


anvil.server._register_exception_type("tables.TransactionConflict", TransactionConflict)
anvil.server._register_exception_type("tables.TableError", TableError)


class Transaction:
	def __init__(self):
		self._aborting = False

	#!defMethod(tables.Transaction instance)!2: "Begin the transaction" ["__enter__"]
	def __enter__(self):
		anvil.server.call("anvil.private.tables.open_transaction")
		return self

	#!defMethod(_)!2: "End the transaction" ["__exit__"]
	def __exit__(self, e_type, e_val, tb):
		anvil.server.call("anvil.private.tables.close_transaction", self._aborting or e_val is not None)

	#!defMethod(_)!2: "Abort this transaction. When it ends, all write operations performed during it will be cancelled"
	def abort(self):
		self._aborting = True
#!defClass(tables,Transaction)!:


def set_client_config(x):
    pass
