import logging

import spacy
from spacy import Language
from spacy_langdetect import LanguageDetector

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

	language_detector = get_language_detector()
	for id_ in page_ids:
		page = pages.get(id_)
		page_language = language_detector(page.text)._.language.get("language")
		if page_language is not None:
			log.info(f"Язык страницы {page.url}: {page_language}")
		else:
			log.warning("Не смог определить язык страницы " + page.url)
			continue

		raise NotImplementedError()


def get_language_detector():
	@Language.factory("language_detector")
	def create_language_detector(nlp, name):
		return LanguageDetector()

	language_detector = spacy.blank("en")
	language_detector.add_pipe("sentencizer")
	language_detector.add_pipe("language_detector")
	return language_detector


if __name__ == '__main__':
	main()
