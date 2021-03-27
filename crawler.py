import logging
import os
import sys
from collections import deque
from urllib.parse import urljoin

import requests
import validators
from bs4 import BeautifulSoup

from implementation.common import delete_extra_whitespaces
from implementation.infrastructure import configure_logging, format_exception
from implementation.raw_document import RawDocument, RawDocumentRepository, raw_texts_repository_name

log = logging.getLogger()

max_pages_count = 100
min_words_per_page_count = 1000


def main():
	root_page_url = get_root_page_url_or_print_help()
	if root_page_url is None:
		return

	configure_logging()
	
	run(root_page_url)


def run(root_page_url):
	log.info("Инициализирую хранилище страниц")
	pages = RawDocumentRepository(raw_texts_repository_name)
	pages.delete_all()

	page_urls_to_download = deque([root_page_url])
	seen_page_urls = {root_page_url}
	downloaded_pages = {}
	while len(page_urls_to_download) > 0 and len(downloaded_pages) < max_pages_count:
		page_url = page_urls_to_download.popleft()
		log.info("Скачиваю страницу " + page_url)
		page = download(page_url, seen_page_urls)
		if page is None:
			continue
		if issubclass(type(page), Exception):
			log.warning(f"Не смог скачать страницу {page_url}:" + os.linesep + format_exception(page))
			continue

		try:
			page_html = BeautifulSoup(page, "html.parser")
		except Exception as exception:
			log.warning(
				f"Не смог распознать страницу {page_url} как HTML:" + os.linesep
				+ format_exception(exception) + os.linesep + "Полученная страница:" + os.linesep + page)
			continue

		page_text = get_text(page_html)
		if count_words(page_text) >= min_words_per_page_count:
			downloaded_pages[page_url] = page_text

			log.info("Сохраняю страницу " + page_url)
			id_ = pages.get_new_id()
			page = RawDocument(id_, page_url, page_text)
			try:
				pages.create(page)
			except Exception as exception:
				log.error(
					f"Не смог сохранить страницу {page_url} под номером {id_}:" + os.linesep
					+ format_exception(exception))

		child_urls = set(get_link_urls(page_url, page_html))
		child_urls = child_urls.difference(seen_page_urls)

		page_urls_to_download.extend(child_urls)
		seen_page_urls = seen_page_urls.union(child_urls)


def get_root_page_url_or_print_help():
	if len(sys.argv) != 2:
		print(f"Использование: {sys.argv[0]} <URL индексируемой страницы>")
		return None

	return sys.argv[1]


def download(url, seen_page_urls):
	try:
		response = requests.get(url, headers = {"accept": "text/html"}, stream = True)

		if response.url != url and response.url in seen_page_urls:
			return None

		content_type = response.headers.get("content-type")
		if content_type is None or len(content_type) == 0:
			return ValueError("Получил страницу с пустым Content-Type")
		if "html" not in content_type:
			return ValueError("Получил страницу с неизвестным Content-Type: " + content_type)

		return response.text
	except Exception as error:
		return error


def get_link_urls(current_url, html):
	if html.body is None:
		return []

	a_tags = html.body.find_all("a")
	urls = (tag.get("href", default = "") for tag in a_tags)
	urls = (urljoin(current_url, url) for url in urls)
	valid_urls = filter(lambda url: validators.url(url), urls)
	return valid_urls


def get_text(html):
	text = html.get_text(" ")
	text = delete_extra_whitespaces(text)
	return text


def count_words(text):
	return len(text.split())


if __name__ == '__main__':
	main()
