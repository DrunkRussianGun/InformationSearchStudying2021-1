from tinydb import table

from implementation.infrastructure import get_tinydb_table

inversed_index_repository_path = "inversed_index"


class InversedIndexRepository:
	def __init__(self, name):
		self.__table = get_tinydb_table(name + ".json")

	def get(self):
		return self.__table.table().get(doc_id = 0)

	def save(self, index):
		if self.__table.contains(doc_id = 0):
			self.__table.remove(doc_ids = [0])
		self.__table.insert(table.Document(index, doc_id = 0))
