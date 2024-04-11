import copy


USAGE = '$usage'


_g_funcs = {}
_g_usages = {}
_g_logger = None


def register(itdef, func):
    name = itdef[USAGE]
    _g_usages[name] = itdef
    _g_funcs[name] = func

def load_wasm(wasm_path, page_num):
    from smwasm.wasm import load
    load.load_wasm(wasm_path, page_num)

def get(usage, dt):
    item = _g_usages.get(usage)
    if item == None:
        return None

    ret = copy.deepcopy(item)

    for key in dt:
        v = dt[key]
        ret[key] = v
    return ret

def use(dt):
    usage = dt.get(USAGE)
    func = _g_funcs.get(usage)
    dtRet = func(dt)
    return dtRet

def call(usage, dt):
    dtCall = get(usage, dt)
    dtRet = use(dtCall)
    return dtRet

def log(text):
    if _g_logger:
        _g_logger.info(text)
    else:
        print(text)

def set_logger(logger):
    global _g_logger
    _g_logger = logger
