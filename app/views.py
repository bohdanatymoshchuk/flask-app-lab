import logging
from flask import render_template, redirect, url_for, flash
from app import app
from app.forms import ContactForm

logger = logging.getLogger('contact_logger')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('contact_form.log', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
if not logger.handlers:
    logger.addHandler(file_handler)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    
    if form.validate_on_submit():
        try:
            log_entry = (
                f"Name: {form.name.data} | "
                f"Email: {form.email.data} | "
                f"Phone: {form.phone.data} | "
                f"Subject: {form.subject.data} | "
                f"Message: {form.message.data}"
            )
            logger.info(log_entry)
            
            flash('Ваше повідомлення успішно надіслано та збережено!', 'success')
        except Exception as e:
            logger.error(f"Помилка під час збереження повідомлення: {e}")
            flash('Сталася помилка під час обробки вашої форми.', 'danger')

        # патерн post/redirect/get
        return redirect(url_for('contact'))

    return render_template('contact.html', form=form, title='Контакти')