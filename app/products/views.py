from flask import Blueprint, render_template, abort

from app.products import storage

products_bp = Blueprint(
    'products', __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/product',
)


@products_bp.route('/', strict_slashes=False)
def list_products():
    return render_template('products/products.html', products=storage.get_all(),
                           title='Список товарів')