# --- python 2 special ---

import json
from collections import OrderedDict


class PyBase:

    @staticmethod
    def is_method(attr):
        type_name = type(attr).__name__
        return type_name == "instancemethod"

    @staticmethod
    def load_json(text, object_pairs_hook=OrderedDict):
        return json.loads(text, object_pairs_hook=object_pairs_hook)
