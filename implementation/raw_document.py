from pathlib import Path


class RawDocument:
	def __init__(self, id_, url, text):
		self.id_ = id_
		self.url = url
		self.text = text


raw_texts_repository_name = "raw_texts"


class RawDocumentRepository:
	__file_encoding = "utf-8"

	def __init__(self, name = ""):
		name = name if len(name) > 0 else "default"
		repository_path = Path(name)
		self.__index_full_file_name = repository_path.joinpath("index.txt")
		self.__documents_path = repository_path.joinpath("documents")

		self.__documents_path.mkdir(parents = True, exist_ok = True)
		self.__index_file = open(
			self.__index_full_file_name,
			"a+",
			encoding = RawDocumentRepository.__file_encoding)
		self.__initialize_index_from_file(True)

		self.__max_id = max(self.__id_to_url_map.keys(), default = -1)

	def get_new_id(self):
		self.__max_id += 1
		return self.__max_id

	def get_all_ids(self):
		return self.__id_to_url_map.keys()

	def get(self, id_):
		if id_ not in self.__id_to_url_map.keys():
			return None

		document_full_file_name = self.__get_document_full_file_name(id_)
		with open(document_full_file_name, "r", encoding = RawDocumentRepository.__file_encoding) as file:
			text = file.read()

		url = self.__id_to_url_map[id_]
		return RawDocument(id_, url, text)

	def create(self, document):
		if document.id_ in self.__id_to_url_map:
			raise RuntimeError(
				f"Не смог создать документ с номером {document.id_} в хранилище, "
				+ f"т. к. документ с таким номером уже существует")

		document_full_file_name = self.__get_document_full_file_name(document.id_)
		with open(document_full_file_name, "w", encoding = RawDocumentRepository.__file_encoding) as file:
			file.write(document.text)

		self.__append_index_line_to_file(document.id_, document.url)
		self.__index_file.flush()

		self.__id_to_url_map[document.id_] = document.url

	def delete_all(self):
		if len(self.__id_to_url_map) == 0:
			return

		for id_ in self.__id_to_url_map:
			document_full_file_name = self.__get_document_full_file_name(id_)
			Path(document_full_file_name).unlink(True)

		self.__index_file.truncate(0)
		self.__index_file.flush()

		self.__id_to_url_map = {}
		self.__max_id = -1

	def __initialize_index_from_file(self, recreate_file_if_inconsistent):
		self.__index_file.seek(0)
		file_lines = self.__index_file.readlines()

		self.__id_to_url_map = {}
		for file_line in file_lines:
			index_line = self.__parse_file_line(file_line)
			id_, url = int(index_line[0]), index_line[1]

			document_full_file_name = self.__get_document_full_file_name(id_)
			if Path(document_full_file_name).is_file():
				self.__id_to_url_map[id_] = url

		if recreate_file_if_inconsistent and len(self.__id_to_url_map) != len(file_lines):
			self.__recreate_index_file()

	def __recreate_index_file(self):
		self.__index_file.truncate(0)
		for id_, url in self.__id_to_url_map.items():
			self.__append_index_line_to_file(id_, url)
		self.__index_file.flush()

	def __append_index_line_to_file(self, id_, url):
		self.__index_file.write(f"{id_} {url}\n")

	def __get_document_full_file_name(self, id_):
		return self.__documents_path.joinpath(f"{id_}.txt")

	@staticmethod
	def __parse_file_line(file_line):
		return file_line.rstrip("\n").split(" ")
