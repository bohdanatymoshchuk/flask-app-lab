from flask import Blueprint, render_template, redirect, url_for, flash, abort

from app.products import storage
from app.products.forms import ProductForm, CATEGORIES

products_bp = Blueprint(
    'products', __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/product',
)


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
            'price': float(form.price.data),   # Decimal не серіалізується в JSON
            'category': form.category.data,
            'quantity': form.quantity.data,
            'image': None,
        })
        flash('Товар успішно додано!', 'success')
        return redirect(url_for('products.list_products'))   # PRG

    if form.is_submitted():
        flash('Виправте помилки у формі.', 'danger')
    return render_template('products/product_form.html', form=form,
                           product=None, title='Додати товар')