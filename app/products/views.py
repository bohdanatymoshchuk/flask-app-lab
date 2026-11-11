import os
import uuid

from flask import (Blueprint, render_template, redirect, url_for,
                   flash, abort, current_app)
from werkzeug.datastructures import FileStorage

from app.products import storage
from app.products.forms import ProductForm, DeleteForm, CATEGORIES

products_bp = Blueprint(
    'products', __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/product',
)


def has_upload(file_field):
    return isinstance(file_field.data, FileStorage) and bool(file_field.data.filename)


def save_image(file_storage):
    """Зберігає файл під UUID-ім'ям, повертає відносний шлях."""
    ext = file_storage.filename.rsplit('.', 1)[-1].lower()
    filename = f'{uuid.uuid4().hex}.{ext}'
    folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(folder, exist_ok=True)
    file_storage.save(os.path.join(folder, filename))
    return f'uploads/{filename}'


def delete_image(rel_path):
    if not rel_path:
        return
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(rel_path))
    if os.path.isfile(path):
        os.remove(path)


@products_bp.route('/', strict_slashes=False)
def list_products():
    return render_template('products/products.html', products=storage.get_all(),
                           title='Список товарів', categories=dict(CATEGORIES))


@products_bp.route('/add', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        storage.create({
            'name': form.name.data,
            'content': form.content.data,
            'price': float(form.price.data),
            'category': form.category.data,
            'quantity': form.quantity.data,
            'image': save_image(form.image.data) if has_upload(form.image) else None,
        })
        flash('Товар успішно додано!', 'success')
        return redirect(url_for('products.list_products'))

    if form.is_submitted():
        flash('Виправте помилки у формі.', 'danger')
    return render_template('products/product_form.html', form=form,
                           product=None, title='Додати товар')


@products_bp.route('/<int:product_id>')
def detail_product(product_id):
    product = storage.get_by_id(product_id)
    if product is None:
        abort(404)
    return render_template('products/detail_product.html', product=product,
                           categories=dict(CATEGORIES), title=product['name'],
                           delete_form=DeleteForm())


@products_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    product = storage.get_by_id(product_id)
    if product is None:
        abort(404)

    initial = {k: v for k, v in product.items() if k != 'image'}
    form = ProductForm(data=initial)

    if form.validate_on_submit():
        data = {
            'name': form.name.data,
            'content': form.content.data,
            'price': float(form.price.data),
            'category': form.category.data,
            'quantity': form.quantity.data,
        }
        if has_upload(form.image):
            new_path = save_image(form.image.data)
            delete_image(product.get('image'))   # видаляємо старий файл
            data['image'] = new_path
        storage.update(product_id, data)
        flash('Зміни збережено!', 'success')
        return redirect(url_for('products.detail_product', product_id=product_id))

    if form.is_submitted():
        flash('Виправте помилки у формі.', 'danger')
    return render_template('products/product_form.html', form=form,
                           product=product, title='Редагувати товар')


@products_bp.route('/<int:product_id>/delete', methods=['POST'])
def delete_product(product_id):
    if not DeleteForm().validate_on_submit():
        abort(400)
    product = storage.get_by_id(product_id)
    if product is None:
        abort(404)
    delete_image(product.get('image'))
    storage.delete(product_id)
    flash('Товар видалено.', 'success')
    return redirect(url_for('products.list_products'))