import os, json, time, hashlib

CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', 'cache', 'summaries.json')
os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

def _load_cache():
    import os
    if not os.path.exists(CACHE_FILE) or os.path.getsize(CACHE_FILE) == 0:
        return {}
    if os.path.exists(CACHE_FILE):
        return json.load(open(CACHE_FILE, 'r'))
    return {}


def _save_cache(cache):
    json.dump(cache, open(CACHE_FILE, 'w'), indent=2)

def generate_key(paper):
    if paper.get('doi'):
        return paper['doi']
    return hashlib.sha256(paper['title'].encode()).hexdigest()

def get_cached_summary(key):
    cache = _load_cache()
    return cache.get(key)

def set_cached_summary(key, summary,paper):
    cache = _load_cache()
    cache[key] = paper
    _save_cache(cache)

def clear_cache_file():
    with open(CACHE_FILE, 'w') as f:
        f.write('')