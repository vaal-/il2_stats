# from aiohttp_wsgi.api import serve
from waitress import serve

from core.wsgi import application


if __name__ == '__main__':
    from config import HTTP_HOST, HTTP_PORT
    serve(
        app=application,
        host=HTTP_HOST,
        port=HTTP_PORT,
        threads=10,
        ident='IL2 stats',
        asyncore_use_poll=True,
        # cleanup_interval=5,
        # channel_timeout=6,
        max_request_body_size=5242880,  # 5MB
    )
