from pathlib import Path

from tinydb import table

from implementation.infrastructure import get_tinydb_table

tokenized_texts_repository_name = "tokenized_texts"


class TokenizedDocument:
	def __init__(self, id_, url, language_code, tokens):
		self.id_ = id_
		self.url = url
		self.language_code = language_code
		self.tokens = tokens


class TokenizedDocumentRepository:
	__file_encoding = "utf-8"
	__token_separator = "\n"

	def __init__(self, name = ""):
		name = name if len(name) > 0 else "default"
		repository_path = Path(name)
		self.__documents_path = repository_path.joinpath("documents")

		self.__documents_path.mkdir(parents = True, exist_ok = True)
		self.__table = get_tinydb_table(repository_path.joinpath("index.json"))
		self.__check_and_correct_table()

	def get_all_ids(self):
		return [document.doc_id for document in self.__table.all()]

	def get(self, id_):
		document_properties = self.__table.get(doc_id = id_)
		if document_properties is None:
			return None

		document = object.__new__(TokenizedDocument)
		vars(document).update(document_properties)
		document.id_ = id_

		document_full_file_name = self.__get_document_full_file_name(id_)
		with open(
				document_full_file_name,
				"r",
				encoding = TokenizedDocumentRepository.__file_encoding) as file:
			document.tokens = file.read().split(TokenizedDocumentRepository.__token_separator)

		return document

	def create(self, document):
		if self.__table.contains(doc_id = document.id_):
			raise RuntimeError(
				f"Не смог создать документ с номером {document.id_} в хранилище, "
				+ f"т. к. документ с таким номером уже существует")

		document_properties = dict(vars(document))
		document_properties.pop("id_")
		document_properties.pop("tokens")
		self.__table.insert(table.Document(document_properties, doc_id = document.id_))

		document_full_file_name = self.__get_document_full_file_name(document.id_)
		with open(
				document_full_file_name,
				"w",
				encoding = TokenizedDocumentRepository.__file_encoding) as file:
			file.write(TokenizedDocumentRepository.__token_separator.join(document.tokens))

	def delete_all(self):
		for document in self.__table.all():
			document_full_file_name = self.__get_document_full_file_name(document.doc_id)
			Path(document_full_file_name).unlink(True)

		self.__table.truncate()

	def __get_document_full_file_name(self, id_):
		return self.__documents_path.joinpath(f"{id_}.txt")

	def __check_and_correct_table(self):
		for id_ in self.get_all_ids():
			document_full_file_name = self.__get_document_full_file_name(id_)
			if not Path(document_full_file_name).is_file():
				self.__table.remove(doc_ids = [id_])
