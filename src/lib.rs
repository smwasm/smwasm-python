use pyo3::prelude::*;
use pyo3::types::PyModule;
use std::sync::{RwLock, Arc};
use once_cell::sync::Lazy;

use smcore::{smh, smu};
use smdton::{SmDton, SmDtonBuffer, SmDtonBuilder, SmDtonMap};

static SME_MODULE: Lazy<Arc<RwLock<Option<Py<PyAny>>>>> = Lazy::new(|| {
    Arc::new(RwLock::new(None))
});

#[pyfunction]
pub fn rs_load_wasm(_py: Python, wasm: &str, space: i32) {
    smloadwasm::load_wasm(wasm, space);
}

#[pyfunction]
pub fn rs_call(_py: Python, txt: &str) -> PyResult<String> {
    let jsn = json::parse(txt).unwrap();
    let smb = smu.build_buffer(&jsn);
    let ret = smh.call(smb);

    if let Some(txt) = ret.stringify() {
        Ok(txt)
    } else {
        Ok("{}".to_string())
    }
}

#[pyfunction]
pub fn rs_register_native(_py: Python, txt: &str) -> PyResult<bool> {
    let define = json::parse(txt).unwrap();
    smh.register_by_json(&define, _call_sm);
    Ok(true)
}

#[pymodule]
fn smwasm(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    smloadwasm::init();
    smsys::init();

    m.add_function(wrap_pyfunction!(rs_load_wasm, m)?)?;
    m.add_function(wrap_pyfunction!(rs_call, m)?)?;
    m.add_function(wrap_pyfunction!(rs_register_native, m)?)?;

    let smh_module: Bound<'_, PyModule> = py.import("smwasm.smh")?;
    *SME_MODULE.write().unwrap() = Some(smh_module.into());

    Ok(())
}

fn _call_sm(_input: &SmDtonBuffer) -> SmDtonBuffer {
    let mut result_str = "{}".to_string();

    Python::attach(|py| {
        let guard = SME_MODULE.read().unwrap();
        if let Some(sme_module) = guard.as_ref() {
            if let Ok(func) = sme_module.getattr(py, "call_native") {
                let sd = SmDton::new_from_buffer(_input);
                let intxt = sd.stringify().unwrap_or_else(|| "{}".to_string());

                if let Ok(result) = func.call1(py, (intxt,)) {
                    if let Ok(response) = result.extract::<String>(py) {
                        result_str = response;
                    }
                }
            }
        }
    });

    if let Ok(jsn) = json::parse(&result_str) {
        SmDtonBuilder::new_from_json(&jsn).build()
    } else {
        SmDtonMap::new().build()
    }
}
