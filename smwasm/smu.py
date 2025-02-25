import time
import json
import codecs
import os

try:
    import yaml
except:
    pass

from smwasm.base._py_base import pybase


def current():
    lt = time.gmtime(time.time() - time.timezone)
    return time.strftime("%Y-%m-%d %H:%M:%S", lt)


def dict_to_format_json(dictData, indent):
    txt = ""
    try:
        txt = json.dumps(dictData, ensure_ascii=False, indent=indent)
    except:
        pass
    return txt


def json_to_dict(text):
    if not text:
        return None

    dt = json.loads(text)
    return dt


def read_file(fileName):
    fileData = ""
    if os.path.exists(fileName):
        try:
            f = codecs.open(fileName, "r", "utf8")
            fileData = f.read()
            f.close()
        except:
            pass
    return fileData


def read_json(fileName):
    fileData = read_file(fileName)
    if fileData:
        try:
            dictData = pybase.load_json(fileData)
            return dictData
        except:
            try:
                dictData = yaml.load(fileData, Loader=yaml.FullLoader)
                return dictData
            except:
                try:
                    dictData = yaml.load(fileData)
                    return dictData
                except:
                    return None
    return None


def write_json(fileName, jsonData, codePage="utf8"):
    jsonString = json.dumps(jsonData, ensure_ascii=False, indent=2).encode(codePage)
    f = open(fileName, "wb")
    f.write(jsonString)
    f.close()
