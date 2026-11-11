from decimal import Decimal

from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, DecimalField, SelectField,
                     IntegerField, SubmitField)
from wtforms.validators import (DataRequired, InputRequired, Length,
                                NumberRange, ValidationError)

CATEGORIES = [
    ('electronics', 'Електроніка'),
    ('clothes', 'Одяг'),
    ('books', 'Книги'),
    ('home', 'Дім і сад'),
    ('other', 'Інше'),
]


def two_decimal_places(form, field):
    """Ціна — не більше двох знаків після коми."""
    if field.data is None:
        return
    exp = field.data.as_tuple().exponent
    if isinstance(exp, int) and exp < -2:
        raise ValidationError('Ціна може мати не більше двох знаків після коми.')


class ProductForm(FlaskForm):
    name = StringField('Назва', validators=[
        DataRequired(message='Вкажіть назву товару.'),
        Length(min=3, max=100, message='Назва має містити щонайменше 3 символи.'),
    ])
    content = TextAreaField('Опис', render_kw={'rows': 5, 'cols': 40}, validators=[
        DataRequired(message='Додайте опис товару.'),
    ])
    price = DecimalField('Ціна', places=2, validators=[
        InputRequired(message='Вкажіть ціну.'),
        NumberRange(min=Decimal('0.01'), message='Ціна має бути додатною.'),
        two_decimal_places,
    ])
    category = SelectField('Категорія', choices=CATEGORIES, validators=[
        DataRequired(message='Оберіть категорію.'),
    ])
    quantity = IntegerField('Кількість', validators=[
        InputRequired(message='Вкажіть кількість.'),
        NumberRange(min=0, message='Кількість не може бути від’ємною.'),
    ])
    submit = SubmitField('Зберегти')


class DeleteForm(FlaskForm):
    """Порожня форма: потрібна лише для CSRF-токена при видаленні."""
    submit = SubmitField('Видалити')