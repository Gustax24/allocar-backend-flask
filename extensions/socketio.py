import os
from flask_socketio import SocketIO

# Utilise un mode compatible par défaut (threading).
# Tu peux changer via l'env: SOCKETIO_ASYNC_MODE=eventlet|gevent|threading
ASYNC_MODE = os.getenv("SOCKETIO_ASYNC_MODE", "threading")

socketio = SocketIO(async_mode=ASYNC_MODE)
