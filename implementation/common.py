import re as regex

import en_core_web_md
import ru_core_news_md

available_language_codes = {"en", "ru"}
language_processors_cache = {}


def get_language_processor(language_code, **load_kwargs):
	processor = language_processors_cache.get(language_code)
	if processor is not None:
		return processor

	if language_code not in available_language_codes:
		return None
	if language_code == "en":
		processor = en_core_web_md.load(**load_kwargs)
	elif language_code == "ru":
		processor = ru_core_news_md.load(**load_kwargs)
	else:
		processor = None

	language_processors_cache[language_code] = processor
	return processor


def delete_extra_whitespaces(text):
	text = text.strip()

	# Заменяем каждую последовательность пробельных символов на единственный пробел,
	# за исключением переносов строк
	text = regex.sub("((?!\\n)\\s)+", " ", text)
	# Убираем пробельные символы вокруг переносов строк
	# и заменяем каждую последовательность переносов строк на единственный перенос строки
	text = regex.sub("\\s*\\n\\s*", "\n", text)

	return text
