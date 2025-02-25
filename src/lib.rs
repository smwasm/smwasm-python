use json::JsonValue;
use pyo3::prelude::*;
use std::sync::{RwLock, Arc};
use once_cell::sync::Lazy;

use smcore::{smh, smu};
use smdton::{SmDton, SmDtonBuffer, SmDtonBuilder, SmDtonMap};

static SME_MODULE: Lazy<Arc<RwLock<Option<PyObject>>>> = Lazy::new(|| {
    Arc::new(RwLock::new(None))
});

#[pyfunction]
pub fn rs_load_wasm(_py: Python, wasm: &str, space: i32) {
    smloadwasm::load_wasm(wasm, space);
}

#[pyfunction]
pub fn rs_call(_py: Python, txt: &str) -> PyResult<String> {
    let mut rtext = "{}".to_string();

    let jsn = json::parse(txt).unwrap();
    let smb = smu.build_buffer(&jsn);
    let ret = smh.call(smb);

    let op_ret = ret.stringify();
    match op_ret {
        Some(txt) => {
            rtext = txt;
        },
        None => {
        },
    }

    Ok(rtext)
}

#[pyfunction]
pub fn rs_register_native(_py: Python, txt: &str) -> PyResult<bool> {
    let _define = json::parse(txt).unwrap();
    smh.register_by_json(&_define, _call_sm);

    Ok(true)
}

#[pymodule]
fn smwasm(_py: Python, m: &PyModule) -> PyResult<()> {
    smloadwasm::init();
    smsys::init();

    m.add_function(wrap_pyfunction!(rs_load_wasm, m)?)?;
    m.add_function(wrap_pyfunction!(rs_call, m)?)?;
    m.add_function(wrap_pyfunction!(rs_register_native, m)?)?;

    let _smh: Result<&PyModule, PyErr> = _py.import("smwasm.smh");
    let _sme_module: &PyModule = _smh?;
    *SME_MODULE.write().unwrap() = Some(_sme_module.into());

    Ok(())
}

fn _call_sm(_input: &SmDtonBuffer) -> SmDtonBuffer {
    let mut result_str = "{}".to_string();

    Python::with_gil(|py| {
        let sme_module_guard = SME_MODULE.read().unwrap();

        if let Some(sme_module) = sme_module_guard.as_ref() {
            match sme_module.getattr(py, "call_native") {
                Ok(func) => {
                    let sd = SmDton::new_from_buffer(_input);
                    let intxt = sd.stringify();

                    match func.call1(py, (intxt,)) {
                        Ok(py_any) => {
                            let py_any_ref: &PyAny = py_any.as_ref(py);

                            match py_any_ref.extract::<String>() {
                                Ok(response) => {
                                    result_str = response;
                                }
                                Err(_e) => {
                                }
                            }
                        }
                        Err(_e) => {
                        }
                    }
                }
                Err(_e) => {
                }
            }
        } else {
        }
    });

    let parsed: Result<JsonValue, json::Error> = json::parse(&result_str);
    match parsed {
        Ok(jsn) => {
            let mut sdb = SmDtonBuilder::new_from_json(&jsn);
            return sdb.build();
        }
        Err(_e) => {
        }
    }

    let mut _map = SmDtonMap::new();
    return _map.build();
}
