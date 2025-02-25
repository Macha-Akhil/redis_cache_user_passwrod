# from flask import Flask, request, jsonify
# from flask_caching import Cache

# app = Flask(__name__)

# # Configure the cache with Redis
# app.config['CACHE_TYPE'] = 'redis'
# app.config['CACHE_REDIS_HOST'] = 'localhost'
# app.config['CACHE_REDIS_PORT'] = 6379
# app.config['CACHE_REDIS_DB'] = 0
# app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'
# cache = Cache(app)

# @app.route('/data')
# @cache.cached(timeout=120)  # Cache this endpoint for 60 seconds
# def get_data():
#     # Simulate an expensive computation or database query
#     data = {'message': 'Hello, world!'}
#     return jsonify(data)

# @app.route('/clear_cache')
# def clear_cache():
#     cache.clear()
#     return 'Cache cleared!'

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, request, jsonify, make_response
from flask_caching import Cache

app = Flask(__name__)

# Configure the cache with Redis
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_HOST'] = 'localhost'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_REDIS_DB'] = 0
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'
cache = Cache(app)

@app.route('/data')
@cache.cached(timeout=120)
def get_data():
    # Simulate an expensive computation or database query
    data = {'message': 'Hello, world!'}
    response = make_response(jsonify(data))
    response.headers['X-Cache'] = 'MISS'
    return response

@app.route('/clear_cache')
def clear_cache():
    cache.clear()
    return 'Cache cleared!'

@app.after_request
def apply_caching(response):
    if 'X-Cache' not in response.headers:
        response.headers['X-Cache'] = 'HIT'
    return response

if __name__ == '__main__':
    app.run(debug=True)
