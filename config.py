import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-lab4'

PRODUCTS_DB_PATH = os.path.join(BASE_DIR, 'data', 'products.json')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'products', 'static', 'uploads')
MAX_IMAGE_SIZE = 2 * 1024 * 1024                       # 2 МБ на зображення
MAX_CONTENT_LENGTH = MAX_IMAGE_SIZE + 512 * 1024       # жорсткий ліміт запиту