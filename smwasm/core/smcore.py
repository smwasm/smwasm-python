
USAGE = "$usage"

g_funcs = {}
g_paths = {}
g_usages = {}

def call_sm(dt):
    usage = dt.get(USAGE)
    if usage in g_funcs:
        func = g_funcs.get(usage)
        dtRet = func(dt)
        return dtRet
    return None
