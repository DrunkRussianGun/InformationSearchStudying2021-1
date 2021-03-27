import logging
import os
import re as regex
import string

import spacy
from spacy import Language
from spacy_langdetect import LanguageDetector

from implementation.common import get_language_processor
from implementation.infrastructure import configure_logging, format_exception
from implementation.raw_document import RawDocumentRepository, raw_texts_repository_name
from implementation.tokenized_document import TokenizedDocument, TokenizedDocumentRepository, \
	tokenized_texts_repository_name

log = logging.getLogger()

punctuation_whitespacing_map = {ord(symbol): " " for symbol in string.punctuation + "«»—–“”•☆№\""}


def main():
	configure_logging()

	run()


def run():
	log.info("Инициализирую хранилище страниц")
	pages = RawDocumentRepository(raw_texts_repository_name)
	page_ids = pages.get_all_ids()

	log.info("Инициализирую хранилище токенизированных текстов")
	tokenized_texts = TokenizedDocumentRepository(tokenized_texts_repository_name)
	tokenized_texts.delete_all()

	language_detector = get_language_detector()
	for id_ in page_ids:
		page = pages.get(id_)
		page.text = preprocess_text(page.text)

		page_language = language_detector(page.text)._.language.get("language")
		if page_language is not None:
			log.info(f"Язык страницы {page.url}: {page_language}")
		else:
			log.warning("Не смог определить язык страницы " + page.url)
			continue

		language_processor = get_language_processor(page_language)
		if language_processor is None:
			log.error("Не нашёл обработчик языка " + page_language)
			continue
		lemmas = [token.lemma_
			for token in language_processor(page.text)
			if not str.isspace(token.lemma_)]

		document = TokenizedDocument(id_, page.url, page_language, lemmas)
		try:
			tokenized_texts.create(document)
		except Exception as exception:
			log.error(
				f"Не смог сохранить токенизированный текст страницы {page.url}:" + os.linesep
				+ format_exception(exception))


def get_language_detector():
	@Language.factory("language_detector")
	def create_language_detector(nlp, name):
		return LanguageDetector()

	language_detector = spacy.blank("en")
	language_detector.add_pipe("sentencizer")
	language_detector.add_pipe("language_detector")
	return language_detector


def preprocess_text(text):
	# Убираем URL
	text = regex.sub("((https?|ftp)://|(www|ftp)\\.)?[a-z0-9-]+(\\.[a-z0-9-]+)+([/?].*)?", " ", text)
	# Меняем знаки пунктуации на пробелы
	text = text.translate(punctuation_whitespacing_map)

	return text


if __name__ == '__main__':
	main()
