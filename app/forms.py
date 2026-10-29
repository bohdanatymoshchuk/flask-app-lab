from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp

class ContactForm(FlaskForm):
    name = StringField('Ім\'я', validators=[
        DataRequired(message="Це поле є обов'язковим."),
        Length(min=4, max=10, message="Ім'я має містити від 4 до 10 символів.")
    ])

    email = StringField('Email', validators=[
        DataRequired(message="Це поле є обов'язковим."),
        Email(message="Введіть коректну електронну адресу.")
    ])

    phone = StringField('Телефон', validators=[
        DataRequired(message="Це поле є обов'язковим."),
        Regexp(r'^\+380\d{9}$', message="Формат телефону повинен бути: +380XXXXXXXXX")
    ])

    subject = SelectField('Тема', choices=[
        ('general', 'Загальне питання'),
        ('support', 'Технічна підтримка'),
        ('commercial', 'Комерційна пропозиція')
    ], validators=[DataRequired(message="Оберіть тему звернення.")])

    message = TextAreaField('Повідомлення', validators=[
        DataRequired(message="Це поле є обов'язковим."),
        Length(max=500, message="Довжина повідомлення не повинна перевищувати 500 символів.")
    ])

    submit = SubmitField('Send Message')