import sys


def main():
	root_page_url = get_root_page_url_or_print_help()
	if root_page_url is None:
		return


def get_root_page_url_or_print_help():
	if len(sys.argv) != 2:
		print(f"Использование: {sys.argv[0]} <URL индексируемой страницы>")
		return None

	return sys.argv[1]


if __name__ == '__main__':
	main()
