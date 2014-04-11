import sys
import traceback


if sys.version_info[0] >= 3:
    PY3 = True
    unicode_type = str

    def format_exc(tb):
        return traceback.format_exc()

else:
    unicode_type = unicode

    def format_exc(tb):
        return traceback.format_exc(tb)
