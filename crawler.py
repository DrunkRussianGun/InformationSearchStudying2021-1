import logging
import sys
from collections import deque
from urllib.parse import urljoin

import requests
import validators
from bs4 import BeautifulSoup

max_pages_count = 100


def main():
	root_page_url = get_root_page_url_or_print_help()
	if root_page_url is None:
		return

	configure_logging()

	page_urls_to_download = deque([root_page_url])
	seen_page_urls = {root_page_url}
	downloaded_pages = {}
	while len(page_urls_to_download) > 0 and len(downloaded_pages) < max_pages_count:
		page_url = page_urls_to_download.popleft()
		logging.info("Скачиваю страницу " + page_url)
		page = download(page_url)
		page = BeautifulSoup(page, "html.parser")

		downloaded_pages[page_url] = page
		
		child_urls = set(get_link_urls(page_url, page))
		child_urls = child_urls.difference(seen_page_urls)

		page_urls_to_download.extend(child_urls)
		seen_page_urls = seen_page_urls.union(child_urls)


def get_root_page_url_or_print_help():
	if len(sys.argv) != 2:
		print(f"Использование: {sys.argv[0]} <URL индексируемой страницы>")
		return None

	return sys.argv[1]


def configure_logging():
	log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
	root_logger = logging.getLogger()
	root_logger.setLevel(logging.DEBUG)

	console_handler = logging.StreamHandler()
	console_handler.setFormatter(log_formatter)
	console_handler.setLevel(logging.INFO)
	root_logger.addHandler(console_handler)


def download(url):
	response = requests.get(url, headers = {"accept": "text/html"}, stream = True)

	content_type = response.headers.get("content-type")
	if content_type is None or "html" not in content_type:
		return None

	return response.text


def get_link_urls(current_url, html):
	if html.body is None:
		return []

	a_tags = html.body.find_all("a")
	urls = (tag.get("href", default = "") for tag in a_tags)
	urls = (urljoin(current_url, url) for url in urls)
	valid_urls = filter(lambda url: validators.url(url), urls)
	return valid_urls


if __name__ == '__main__':
	main()
