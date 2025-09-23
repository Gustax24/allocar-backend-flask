import os
from dotenv import dotenv_values

def load_all_env():
    base = dotenv_values(".env")
    local = dotenv_values(".env.local")
    merged = {**base, **local}
    for k, v in merged.items():
        #
        if v is not None:
            os.environ.setdefault(k, str(v))

load_all_env()