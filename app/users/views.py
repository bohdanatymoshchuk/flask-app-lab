from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response

users_bp = Blueprint('users', __name__, template_folder='templates')

USERS_DATA = {
    "admin": "1234",
    "user1": "password"
}

@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in USERS_DATA and USERS_DATA[username] == password:
            session['username'] = username
            flash('Ви успішно авторизувалися!', 'success')
            return redirect(url_for('users.profile'))
        else:
            flash('Wrong data! Try again!', 'danger')
            return redirect(url_for('users.login'))

    return render_template('users/login.html', title='Вхід')


@users_bp.route('/profile', methods=['GET'])
def profile():
    if 'username' not in session:
        flash('Будь ласка, увійдіть у систему для доступу до профілю!', 'danger')
        return redirect(url_for('users.login'))

    current_cookies = request.cookies
    return render_template('users/profile.html', 
                           title='Профіль', 
                           username=session['username'], 
                           cookies=current_cookies)


@users_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    flash('Ви вийшли з системи.', 'info')
    return redirect(url_for('users.login'))

@users_bp.route('/add_cookie', methods=['POST'])
def add_cookie():
    if 'username' not in session:
        return redirect(url_for('users.login'))

    key = request.form.get('key')
    value = request.form.get('value')
    max_age = request.form.get('max_age', type=int)

    resp = make_response(redirect(url_for('users.profile')))
    if key and value:
        resp.set_cookie(key, value, max_age=max_age if max_age else 3600)
        flash(f'Кука "{key}" успішно додана!', 'success')
    else:
        flash('Заповніть ключ та значення!', 'warning')
    return resp


@users_bp.route('/delete_cookie', methods=['POST'])
def delete_cookie():
    if 'username' not in session:
        return redirect(url_for('users.login'))

    key = request.form.get('key')
    resp = make_response(redirect(url_for('users.profile')))
    if key:
        resp.delete_cookie(key)
        flash(f'Кука "{key}" успішно видалена!', 'success')
    return resp


@users_bp.route('/delete_all_cookies', methods=['POST'])
def delete_all_cookies():
    if 'username' not in session:
        return redirect(url_for('users.login'))

    resp = make_response(redirect(url_for('users.profile')))
    
    for key in request.cookies:
        if key != 'session':
            resp.delete_cookie(key)
    flash('Усі користувацькі кукі видалено!', 'success')
    return resp

@users_bp.route('/set_theme/<theme>', methods=['GET'])
def set_theme(theme):
    resp = make_response(redirect(url_for('users.profile')))
    if theme in ['light', 'dark']:
        resp.set_cookie('theme', theme, max_age=3600*24*30)
        flash(f'Встановлено тему: {theme}', 'info')
    return resp