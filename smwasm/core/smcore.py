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
            txt = "{0}\n{1}".format(str(e), traceback.format_exc())
            return {"$panic": txt}
    return None
