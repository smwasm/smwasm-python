import smh
import smu

#------------------------------------------------------------

SM_DOMAIN = 'test'

def _sm_get_text(dt):
    ret = {'text': dt['text'] + '--abc123'}
    return ret

def book():
    itdef_get_text = {'$usage': SM_DOMAIN + '.get.text', 'text': ''}
    smh.register(itdef_get_text, _sm_get_text)

#------------------------------------------------------------

def test():
    current = smu.current()
    print('--- start --- {0} ---'.format(current))
    smh.log('--- log something ---')

    dt = smh.call('test.get.text', {'text': 'abc'})
    print('--- {0} ---'.format(dt))


if __name__ == '__main__':

    book()
    test()
