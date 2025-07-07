import copy
import traceback

from .smwasm import rs_load_wasm, rs_call, rs_register_native
from smwasm.core.smcore import USAGE, g_funcs, g_paths, g_usages, call_sm
from smwasm import smu


_g_logger = None


def register(itdef, path, func):
    name = itdef[USAGE]
    g_usages[name] = itdef
    g_funcs[name] = func
    g_paths[name] = path
    rs_register_native(smu.dict_to_format_json(itdef, 2))

def load_wasm(wasm_path, page_num):
    rs_load_wasm(wasm_path, page_num)


def call(dt):
    dtRet = call_sm(dt)
    if dtRet is None:
        try:
            txt = rs_call(smu.dict_to_format_json(dt, 2))
            dtRet = smu.json_to_dict(txt)
        except Exception as e:
            txt = traceback.format_exc()
            dtRet = {"$panic": txt}
    return dtRet


def call_native(intxt):
    dt = smu.json_to_dict(intxt)
    dtRet = call_sm(dt)
    if dtRet is None:
        return '{}'
    outtxt = smu.dict_to_format_json(dtRet, 2)
    return outtxt


def info():
    ret = {"function": g_paths}
    return ret


def log(text):
    if _g_logger:
        _g_logger.info(text)
    else:
        print(text)


def set_logger(logger):
    global _g_logger
    _g_logger = logger
