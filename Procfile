# web: gunicorn -w 1 --threads 100 app:app
web: gunicorn --worker-class eventlet -w 1 app:app
# web: gunicorn -k gevent -w 1 app:app
# web: gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 app:app