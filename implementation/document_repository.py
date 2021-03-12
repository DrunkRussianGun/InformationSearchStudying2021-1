from pathlib import Path

from implementation.singleton import Singleton


class Document:
	def __init__(self, id_, url, text):
		self.id_ = id_
		self.url = url
		self.text = text


class DocumentRepository(metaclass = Singleton):
	__file_encoding = "utf-8"
	__documents_dir = "documents"

	def __init__(self):
		self.__index = open("index.txt", "a+", encoding = DocumentRepository.__file_encoding)
		self.__index.seek(0)
		Path(DocumentRepository.__documents_dir).mkdir(parents = True, exist_ok = True)

		index_entries = [self.__get_index_entry(line) for line in self.__index.readlines()]
		self.__id_to_url_map = {}
		for id_, url in index_entries:
			path_to_document = self.__get_path_to_document(id_)
			if Path(path_to_document).is_file():
				self.__id_to_url_map[id_] = url

		self.__max_id = max(self.__id_to_url_map.keys(), default = -1)

		if len(self.__id_to_url_map) != len(index_entries):
			self.__index.truncate(0)
			for id_, url in self.__id_to_url_map.items():
				self.__add_index_entry(id_, url)
			self.__index.flush()

	def get_new_id(self):
		self.__max_id += 1
		return self.__max_id

	def get(self, id_):
		raise NotImplementedError()

	def create(self, document):
		if document.id_ in self.__id_to_url_map:
			raise RuntimeError(
				f"Не смог создать документ с номером {document.id_} в хранилище, "
				+ f"т. к. документ с таким номером уже существует")

		path_to_document = self.__get_path_to_document(document.id_)
		with open(path_to_document, "w", encoding = DocumentRepository.__file_encoding) as file:
			file.write(document.text)

		self.__add_index_entry(document.id_, document.url)
		self.__index.flush()

		self.__id_to_url_map[document.id_] = document.url

	def delete_all(self):
		if len(self.__id_to_url_map) == 0:
			return

		for id_ in self.__id_to_url_map:
			path_to_document = self.__get_path_to_document(id_)
			Path(path_to_document).unlink(True)

		self.__index.truncate(0)
		self.__index.flush()

		self.__id_to_url_map = {}
		self.__max_id = -1

	def __add_index_entry(self, id_, url):
		self.__index.write(f"{id_} {url}\n")

	@staticmethod
	def __get_index_entry(file_line):
		splitted_line = file_line.rstrip("\n").split(" ")
		return int(splitted_line[0]), splitted_line[1]

	@staticmethod
	def __get_path_to_document(id_):
		return f"{DocumentRepository.__documents_dir}/{id_}.txt"
