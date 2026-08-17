NUM = 200
COUNTRIES = ['id', 'in', 'ph']
CATEGORIES = ['FINANCE', 'GAME_CASINO', 'GAME_CARD', 'SHOPPING', 'SOCIAL']
CRAW_URL = 'http://127.0.0.1:3300'
CRAW_APPSTORE_URL = 'http://127.0.0.1:3301'

PKGS = [
'tiktok.com',
]

APPSTORE_APPS = [
    "314716233",
]

# Keep compatibility with craw_search.py
CRAW_GOOGLE_STORE_URL = f'{CRAW_URL}/api/apps/'

# country-lang-search
TARGET_DATA = [
    ['id', 'id', 'Pinjaman'],
    ['ng', 'en', 'loan'],
    ['in', 'en', 'loan'],
    ['th', 'th', 'เงินกู้'],
    ['vn', 'vi', 'khoản vay'],
    ['br', 'pt', 'empréstimo'],
]