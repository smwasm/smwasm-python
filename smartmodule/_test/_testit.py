
from smwasm import smh, smu

#------------------------------------------------------------

SM_DOMAIN = 'native'

def _sm_get_text(dt):
    ret = {'text': dt['text'] + '--abc123'}
    return ret

def book():
    itdef_get_text = {'$usage': SM_DOMAIN + '.heart.beat', 'text': ''}
    smh.register(itdef_get_text, _sm_get_text)

    wasm_path = '/git/ee/smmo/web/fserver/data/page/sm/callicum.wasm'
    smh.load_wasm(wasm_path, 33)
    smh.load_wasm('/git/ee/smmo/web/fserver/data/page/sm/smlibr_bg.wasm', 99)
    smh.load_wasm('/git/ee/smmo/web/fserver/data/page/sm/smlibr2_bg.wasm', 99)

#------------------------------------------------------------

def test():
    current = smu.current()
    print('--- start --- {0} ---'.format(current))
    smh.log('--- log something ---')

    dt = smh.call('native.heart.beat', {'text': 'abc'})
    print('--- native.heart.beat --- {0} ---'.format(dt))

    call_text = """
    {
        "$usage": "icu.usage", "$log": false,
        "way": "MessageFormat",
        "locale": "de",
        "format": "At {1,time,::jmm} on {1,date,::dMMMM} ({1,date}), there was {2} on planet {0,number}.",
        "value1": 7,
        "value2": 1675261386000,
        "value3": "a disturbance in the Force"
    }
    """
    dtCall = smu.json_to_dict(call_text)
    dtRet = smh.call("icu.usage", dtCall)
    print('--- test wasm result ---', dtRet)

    call_text = """
    {
        "$usage": "smexample.heart.beat", "$log": false, "text": ">abc>def"
    }
    """
    dtCall = smu.json_to_dict(call_text)
    dtRet = smh.call("smexample.heart.beat", dtCall)
    print('--- test smexample.heart.beat ---', dtCall, '---', dtRet)

    call_text = """
    {
        "$usage": "smtest.wrap.beat", "$log": false
    }
    """
    dtCall = smu.json_to_dict(call_text)
    dtRet = smh.call("smtest.wrap.beat", dtCall)
    print('--- test wrap result 1 ---', dtCall, '---', dtRet)

    dtCall = smu.json_to_dict(call_text)
    dtRet = smh.call("smtest.wrap.beat", dtCall)
    print('--- test wrap result 2 ---', dtCall, '---', dtRet)

    call_text = """
    {
        "$usage": "smtest.native.beat", "$log": false
    }
    """
    dtCall = smu.json_to_dict(call_text)
    dtRet = smh.call("smtest.wrap.beat", dtCall)
    print('--- test native result ---', dtCall, '---', dtRet)


if __name__ == '__main__':

    book()
    test()
