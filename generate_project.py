import os
import json

_base_candidates = [
    "D:/Code/roi-presentation-toolkit",
    os.path.normpath(os.path.dirname(os.path.abspath(__file__))),
    os.path.normpath(os.path.expanduser("~/repos/roi-presentation-toolkit")),
]
BASE = _base_candidates[-1]
for _bp in _base_candidates:
    if os.path.isdir(_bp):
        BASE = _bp
        break
