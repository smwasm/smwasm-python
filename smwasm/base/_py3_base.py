# --- python 3 special ---

import json
from collections import OrderedDict


class PyBase:

    @staticmethod
    def is_method(attr):
        type_name = type(attr).__name__
        return type_name == "method"

    @staticmethod
    def load_json(text, object_pairs_hook=OrderedDict):
        type_name = type(text).__name__
        if type_name == "bytes":
            text = text.decode("utf8")
        return json.loads(text, object_pairs_hook=object_pairs_hook)
