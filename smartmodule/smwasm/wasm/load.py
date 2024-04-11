import time
import struct
import inspect

from wasmtime import Store, Module, Instance, Func, FuncType, ValType

from smwasm import smh, smu


gsn = 0
wasm_pool = {}
method_pool = {}


class WasmLoad():
    def __init__(self, wasm_path, page_num):
        global gsn
        gsn += 1
        self.sn = gsn

        self.wasm_path = wasm_path
        self.page_num = page_num

    def add_func(self, ft, func):
        self.funcs.append(Func(self.store, ft, func))

    def load_wasm(self):
        self.store = Store()
        self.module = Module.from_file(self.store.engine, self.wasm_path)

        self.funcs = []
        imps = self.module.imports
        for one in imps:
            name = one.name
            if name.startswith('__wbg_'):
                name = name[6:len(name) - 17]
            if name == 'hostputmemory':
                self.add_func(FuncType([ValType.i32(), ValType.i32()], []), self.sm_hostputmemory)
            elif name == 'hostcallsm':
                self.add_func(FuncType([ValType.i32()], [ValType.i32()]), self.sm_callsm)
            elif name == 'hostdebug':
                self.add_func(FuncType([ValType.i32(), ValType.i32()], []), self.sm_hostdebug)
            elif name == 'hostgetms':
                self.add_func(FuncType([], [ValType.i64()]), self.sm_hostgetms)
            elif name == 'clock_time_get':
                self.add_func(FuncType([ValType.i32(), ValType.i64(), ValType.i32()], [ValType.i32()]), self.sm_clock_time_get)
            elif name == 'emscripten_notify_memory_growth':
                self.add_func(FuncType([ValType.i32()], []), self.sm_emscripten_notify_memory_growth)
            elif name == 'proc_exit':
                self.add_func(FuncType([ValType.i32()], []), self.sm_proc_exit)
            elif name == 'fd_close':
                self.add_func(FuncType([ValType.i32()], [ValType.i32()]), self.sm_fd_close)
            elif name == 'environ_sizes_get':
                self.add_func(FuncType([ValType.i32(), ValType.i32()], [ValType.i32()]), self.sm_environ_sizes_get)
            elif name == 'environ_get':
                self.add_func(FuncType([ValType.i32(), ValType.i32()], [ValType.i32()]), self.sm_environ_get)
            elif name == 'fd_write':
                self.add_func(FuncType([ValType.i32(), ValType.i32(), ValType.i32(), ValType.i32()], [ValType.i32()]), self.sm_fd_write)
            elif name == 'fd_seek':
                self.add_func(FuncType([ValType.i32(), ValType.i64(), ValType.i32(), ValType.i32()], [ValType.i32()]), self.sm_fd_seek)
            else:
                print('--- need support --- %s ---' % name)

        self.instance = Instance(self.store, self.module, self.funcs)

        iexp = self.instance.exports(self.store)
        self.w_sminit = iexp['sminit']
        self.w_smalloc = iexp['smalloc']
        self.w_smdealloc = iexp['smdealloc']
        self.w_smcall = iexp['smcall']

        memory_export = iexp['memory']
        self.view = memory_export.data_ptr(self.store)
        num = memory_export.grow(self.store, 0)
        num_set = num
        if self.page_num > num:
            memory_export.grow(self.store, self.page_num - num)
            num_set = memory_export.grow(self.store, 0)

        # sm init
        self.w_sminit(self.store, 0)

        wasm_pool[self.wasm_path] = self

        dtCall = {'$usage': 'smker.get.all'}
        dtRet = self.call_wasm(dtCall)
        for one in dtRet:
            smh.register(dtRet[one], self.call_wasm)

        print('+++ %s --- %s [%s-%s] --- loaded ---' % (self.sn, self.wasm_path, num, num_set))

    def call_wasm(self, dt):
        call_text = smu.dict_to_format_json(dt, 2)
        ptr = self.set_input(self.store, call_text)
        ptr_ret = self.w_smcall(self.store, ptr, 1)
        result_text = self.get_output(ptr_ret)
        self.w_smdealloc(self.store, ptr_ret)

        return smu.json_to_dict(result_text)

    #---------------------------------------------------------------------------

    def get_output(self, ptr):
        piece = self.view[ptr : ptr + 4]
        u8a = bytes(piece)
        len = struct.unpack('<I', u8a)[0]

        piece = self.view[ptr + 4 : ptr + 4 + len]
        utf8_bytes = bytes(piece)

        txt = utf8_bytes.decode("utf-8")
        return txt

    def set_input(self, store, txt):
        u8a = txt.encode('utf-8')
        size = len(u8a)
        ptr = self.w_smalloc(self.store, size)
        for k in range(size):
            self.view[ptr + 4 + k] = u8a[k]
        return ptr

    #---------------------------------------------------------------------------

    def sm_hostdebug(self, d1, d2):
        print('+++ %s --- < < --- %s --- %s ---' % (self.sn, d1, d2))

    def sm_hostgetms(self):
        return int(round(time.time() * 1000))

    def sm_hostputmemory(self, ptr, ty):
        if ty != 10:
            return

        message = self.get_output(ptr)
        print('+++ %s %s' % (self.sn, message))

    def sm_callsm(self, ptr):
        txt = self.get_output(ptr)
        dtCall = smu.json_to_dict(txt)
        usage = dtCall.get('$usage')
        dtRet = smh.call(usage, dtCall)
        txt = smu.dict_to_format_json(dtRet, 2)
        ptr = self.set_input(self.store, txt)
        return ptr

    def sm_clock_time_get(self, d1, d2, d3):
        return int(round(time.time() * 1000))

    def sm_emscripten_notify_memory_growth(self):
        print('+++ %s +++ sm --- %s ---' % (self.sn, inspect.currentframe().f_code.co_name))

    def sm_proc_exit(self):
        print('+++ %s +++ sm --- %s ---' % (self.sn, inspect.currentframe().f_code.co_name))

    def sm_fd_close(self):
        print('+++ %s +++ sm --- %s ---' % (self.sn, inspect.currentframe().f_code.co_name))

    def sm_environ_sizes_get(self):
        print('+++ %s +++ sm --- %s ---' % (self.sn, inspect.currentframe().f_code.co_name))

    def sm_environ_get(self):
        print('+++ %s +++ sm --- %s ---' % (self.sn, inspect.currentframe().f_code.co_name))

    def sm_fd_write(self):
        print('+++ %s +++ sm --- %s ---' % (self.sn, inspect.currentframe().f_code.co_name))

    def sm_fd_seek(self):
        print('+++ %s +++ sm --- %s ---' % (self.sn, inspect.currentframe().f_code.co_name))


def load_wasm(wasm_path, page_num):
    if wasm_path in wasm_pool:
        return 1

    obj = WasmLoad(wasm_path, page_num)
    obj.load_wasm()
    return 0

#------------------------------------------------------------

if __name__ == '__main__':

    def test():
        wasm_path = '/git/ee/smmo/web/fserver/data/page/sm/callicum.wasm'
        #smh.load_wasm(wasm_path, 33)
        load_wasm(wasm_path, 22)
        load_wasm('/git/ee/smmo/web/fserver/data/page/sm/smlibr_bg.wasm', 99)
        load_wasm('/git/ee/smmo/web/fserver/data/page/sm/smlibr2_bg.wasm', 99)

        call_text1 = """
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
        call_text2 = """
        {
            "$usage": "icu.usage", "$log": false,
            "way": "NumberFormat",
            "locale": "en",
            "value": 11223344.333
        }
        """
        call_text3 = """
        {
            "$usage": "smexample.heart.beat", "$log": false, "text": "$body"
        }
        """
        call_text4 = """
        {
            "$usage": "smtest.wrap.beat", "$log": false
        }
        """
        dtCall = smu.json_to_dict(call_text3)
        body = ''
        for i in range(2):
            body += '>' + str(i).zfill(9)
        dtCall['text'] = body
        dtRet = smh.call("smexample.heart.beat", dtCall)
        print('--- test smexample.heart.beat ---', dtRet)

        dtCall = smu.json_to_dict(call_text1)
        dtRet = smh.call("icu.usage", dtCall)
        print('--- test result ---', dtRet)

        dtCall = smu.json_to_dict(call_text4)
        dtRet = smh.call("smtest.wrap.beat", dtCall)
        print('--- test wrap result 1 ---', dtRet)

        dtCall = smu.json_to_dict(call_text4)
        dtRet = smh.call("smtest.wrap.beat", dtCall)
        print('--- test wrap result 2 ---', dtRet)

    test()
