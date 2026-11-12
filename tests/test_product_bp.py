import io
import os
import shutil
import tempfile
import unittest

from app import app
from app.products import storage


class ProductCRUDTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._max_image = app.config['MAX_IMAGE_SIZE']
        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            PRODUCTS_DB_PATH=os.path.join(self.tmp, 'products.json'),
            UPLOAD_FOLDER=os.path.join(self.tmp, 'uploads'),
        )
        self.client = app.test_client()

    def tearDown(self):
        app.config['MAX_IMAGE_SIZE'] = self._max_image
        shutil.rmtree(self.tmp, ignore_errors=True)

    # допоміжні методи
    def create_product(self, **override):
        data = {'name': 'Laptop', 'content': 'Потужний ноутбук', 'price': 1200.5,
                'category': 'electronics', 'quantity': 5, 'image': None}
        data.update(override)
        with app.app_context():
            return storage.create(data)

    def get_product(self, pid):
        with app.app_context():
            return storage.get_by_id(pid)

    def all_products(self):
        with app.app_context():
            return storage.get_all()

    @staticmethod
    def form_data(**override):
        data = {'name': 'Laptop', 'content': 'Потужний ноутбук', 'price': '1200.50',
                'category': 'electronics', 'quantity': '5'}
        data.update(override)
        return data

    # Read
    def test_list_empty(self):
        self.assertEqual(self.client.get('/product').status_code, 200)

    def test_list_shows_products(self):
        self.create_product(name='Phone')
        self.assertIn(b'Phone', self.client.get('/product').data)

    def test_detail_page(self):
        pid = self.create_product()
        r = self.client.get(f'/product/{pid}')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'Laptop', r.data)

    def test_detail_not_found(self):
        self.assertEqual(self.client.get('/product/999').status_code, 404)

    # Create
    def test_add_form_page(self):
        self.assertEqual(self.client.get('/product/add').status_code, 200)

    def test_add_product_success(self):
        r = self.client.post('/product/add', data=self.form_data(), follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        self.assertIn('Товар успішно додано'.encode(), r.data)
        items = self.all_products()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['id'], 1)
        self.assertIn('created_at', items[0])
        self.assertEqual(items[0]['price'], 1200.5)

    def test_add_prg_redirect(self):
        r = self.client.post('/product/add', data=self.form_data())
        self.assertEqual(r.status_code, 302)

    def test_add_invalid_name(self):
        r = self.client.post('/product/add', data=self.form_data(name='ab'))
        self.assertEqual(r.status_code, 200)
        self.assertIn('щонайменше 3 символи'.encode(), r.data)
        self.assertEqual(self.all_products(), [])

    def test_add_invalid_price(self):
        for bad in ('0', '-5', '10.999', 'abc'):
            r = self.client.post('/product/add', data=self.form_data(price=bad))
            self.assertEqual(r.status_code, 200, bad)
        self.assertEqual(self.all_products(), [])

    def test_add_negative_quantity(self):
        self.client.post('/product/add', data=self.form_data(quantity='-1'))
        self.assertEqual(self.all_products(), [])

    def test_add_zero_quantity_allowed(self):
        self.client.post('/product/add', data=self.form_data(quantity='0'))
        self.assertEqual(len(self.all_products()), 1)

    def test_add_invalid_category(self):
        self.client.post('/product/add', data=self.form_data(category='nope'))
        self.assertEqual(self.all_products(), [])

    def test_csrf_protection(self):
        app.config['WTF_CSRF_ENABLED'] = True
        self.client.post('/product/add', data=self.form_data())
        self.assertEqual(self.all_products(), [])

    # Images
    def test_add_with_image(self):
        data = self.form_data(image=(io.BytesIO(b'fake'), 'photo.PNG'))
        self.client.post('/product/add', data=data)
        p = self.all_products()[0]
        self.assertTrue(p['image'].startswith('uploads/'))
        self.assertTrue(p['image'].endswith('.png'))
        saved = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(p['image']))
        self.assertTrue(os.path.isfile(saved))

    def test_add_wrong_extension(self):
        data = self.form_data(image=(io.BytesIO(b'fake'), 'anim.gif'))
        self.client.post('/product/add', data=data)
        self.assertEqual(self.all_products(), [])

    def test_add_image_too_large(self):
        app.config['MAX_IMAGE_SIZE'] = 10
        data = self.form_data(image=(io.BytesIO(b'x' * 100), 'big.png'))
        r = self.client.post('/product/add', data=data)
        self.assertIn('завеликий'.encode(), r.data)
        self.assertEqual(self.all_products(), [])

    def test_missing_image_shows_placeholder(self):
        pid = self.create_product(image=None)
        self.assertIn(b'no-image.svg', self.client.get(f'/product/{pid}').data)

    # Update
    def test_edit_form_prefilled(self):
        pid = self.create_product()
        r = self.client.get(f'/product/{pid}/edit')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'value="Laptop"', r.data)

    def test_edit_product(self):
        pid = self.create_product()
        before = self.get_product(pid)
        r = self.client.post(f'/product/{pid}/edit',
                             data=self.form_data(name='Новий', price='99.90'),
                             follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        after = self.get_product(pid)
        self.assertEqual(after['name'], 'Новий')
        self.assertEqual(after['price'], 99.9)
        self.assertEqual(after['id'], before['id'])
        self.assertEqual(after['created_at'], before['created_at'])

    def test_edit_keeps_old_image_when_no_file(self):
        pid = self.create_product(image='uploads/old.png')
        self.client.post(f'/product/{pid}/edit', data=self.form_data())
        self.assertEqual(self.get_product(pid)['image'], 'uploads/old.png')

    def test_edit_replaces_image(self):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        old = os.path.join(app.config['UPLOAD_FOLDER'], 'old.png')
        open(old, 'wb').write(b'1')
        pid = self.create_product(image='uploads/old.png')
        data = self.form_data(image=(io.BytesIO(b'new'), 'new.jpg'))
        self.client.post(f'/product/{pid}/edit', data=data)
        self.assertNotEqual(self.get_product(pid)['image'], 'uploads/old.png')
        self.assertFalse(os.path.exists(old))

    def test_edit_invalid_data_not_saved(self):
        pid = self.create_product()
        self.client.post(f'/product/{pid}/edit', data=self.form_data(name='ab'))
        self.assertEqual(self.get_product(pid)['name'], 'Laptop')

    def test_edit_not_found(self):
        self.assertEqual(self.client.get('/product/999/edit').status_code, 404)

    # Delete
    def test_delete_product(self):
        pid = self.create_product()
        r = self.client.post(f'/product/{pid}/delete')
        self.assertEqual(r.status_code, 302)
        self.assertIsNone(self.get_product(pid))

    def test_delete_get_not_allowed(self):
        pid = self.create_product()
        self.assertEqual(self.client.get(f'/product/{pid}/delete').status_code, 405)
        self.assertIsNotNone(self.get_product(pid))

    def test_delete_removes_image_file(self):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        path = os.path.join(app.config['UPLOAD_FOLDER'], 'x.png')
        open(path, 'wb').write(b'1')
        pid = self.create_product(image='uploads/x.png')
        self.client.post(f'/product/{pid}/delete')
        self.assertFalse(os.path.exists(path))

    def test_delete_not_found(self):
        self.assertEqual(self.client.post('/product/999/delete').status_code, 404)

    # Storage
    def test_ids_are_unique_and_persist(self):
        a = self.create_product(name='AAA')
        b = self.create_product(name='BBB')
        self.assertNotEqual(a, b)
        self.assertTrue(os.path.isfile(app.config['PRODUCTS_DB_PATH']))
        self.assertEqual(len(self.all_products()), 2)


if __name__ == '__main__':
    unittest.main()