from pathlib import Path
import sys

# Гарантируем, что каталог `backend/` есть в sys.path
_BACKEND_DIR = Path(__file__).resolve().parent
_BACKEND_STR = str(_BACKEND_DIR)
if _BACKEND_STR not in sys.path:
    sys.path.insert(0, _BACKEND_STR)

 