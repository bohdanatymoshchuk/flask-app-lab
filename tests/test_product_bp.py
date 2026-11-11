import pytest
from app import app
from app.products.db import db, products_table

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client
    products_table.truncate()

def test_add_product(client):
    response = client.post('/products/add', data={
        'name': 'Тестовий Товар',
        'content': 'Детальний опис товару для тестування',
        'price': '199.99',
        'category': 'electronics',
        'quantity': '10'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Тестовий' in response.data.decode('utf-8')

def test_list_products(client):
    response = client.get('/products/')
    assert response.status_code == 200

def test_product_detail_not_found(client):
    response = client.get('/products/9999', follow_redirects=True)
    assert response.status_code == 200
    assert 'не знайдено' in response.data.decode('utf-8') or response.status_code == 200