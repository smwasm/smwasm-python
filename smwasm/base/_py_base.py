# --- python special ---

import sys

if sys.version_info.major == 2:
    from smwasm.base._py2_base import PyBase
else:
    from smwasm.base._py3_base import PyBase

pybase = PyBase()
