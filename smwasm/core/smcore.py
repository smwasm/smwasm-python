import traceback

USAGE = "$usage"

g_funcs = {}
g_paths = {}
g_usages = {}

def call_sm(dt):
    usage = dt.get(USAGE)
    if usage in g_funcs:
        func = g_funcs.get(usage)
        try:
            dtRet = func(dt)
            return dtRet
        except Exception as e:
            txt = traceback.format_exc()
            return {"$panic": txt}
    return None
