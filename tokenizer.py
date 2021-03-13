import logging

from implementation.document import DocumentRepository, pages_repository_name, tokenized_texts_repository_name
from implementation.infrastructure import configure_logging

log = logging.getLogger()


def main():
	configure_logging()

	run()


def run():
	log.info("Инициализирую хранилище страниц")
	pages = DocumentRepository(pages_repository_name)
	page_ids = pages.get_all_ids()

	log.info("Инициализирую хранилище токенизированных текстов")
	tokenized_texts = DocumentRepository(tokenized_texts_repository_name)

	for id_ in page_ids:
		page = pages.get(id_)
		raise NotImplementedError()


if __name__ == '__main__':
	main()
