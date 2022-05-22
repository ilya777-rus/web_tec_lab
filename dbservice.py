from labapp import db
from datetime import datetime
from flask import session, make_response, redirect, url_for, jsonify
import bcrypt



# Получаем список всех запросов.
def get_contact_req_all():
    result = []     # создаем пустой список
    # Получаем итерируемый объект, где содержатся все строки таблицы contactrequests
    rows = db.session.execute("SELECT * FROM contactrequests").fetchall()
    # Каждую строку конвертируем в стандартный dict, который Flask может трансформировать в json-строку
    for row in rows:
        result.append(dict(row))
    # возвращаем dict, где result - это список с dict-объектов с информацией
    return {'contactrequests': result}


# Получаем запрос с фильтром по id



# Получаем все запросы по имени автора
def get_contact_req_by_author(firstname):
    result = []
    rows = db.session.execute(f"SELECT * FROM contactrequests WHERE firstname = '{firstname}'").fetchall()
    for row in rows:
        result.append(dict(row))
    return {'contactrequests': result}


# Создать новый запрос
def create_contact_req(json_data):
    try:
        cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")     # текущая дата и время
        # INSERT запрос в БД
        db.session.execute(f"INSERT INTO contactrequests "
                           f"(firstname, lastname, email, reqtype, reqtext, createdAt, updatedAt) "
                           f"VALUES ("
                           f"'{json_data['firstname']}', "
                           f"'{json_data['lastname']}', "
                           f"'{json_data['email']}', "
                           f"'{json_data['reqtype']}', "
                           f"'{json_data['reqtext']}', "
                           f"'{cur_time}', "
                           f"'{cur_time}' "               
                           ")")
        # Подтверждение изменений в БД
        db.session.commit()
        # Возвращаем результат
        return {'message': "ContactRequest Created!"}
        # если возникла ошибка запроса в БД
    except Exception as e:
        # откатываем изменения в БД
        db.session.rollback()
        # возвращаем dict с ключом 'error' и текcтом ошибки
        return {'message': str(e)}


# Удалить запрос по id в таблице
def delete_contact_req_by_id(id):
    try:
        # DELETE запрос в БД
        db.session.execute(f"DELETE FROM contactrequests WHERE id = {id}")
        db.session.commit()
        return {'message': "ContactRequest Deleted!"}
    except Exception as e:
        db.session.rollback()
        return {'message': str(e)}


# Обновить текст запроса по id в таблице
def update_contact_req_by_id(id, json_data):
    try:
        cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # текущая дата и время
        # UPDATE запрос в БД
        db.session.execute(f"UPDATE contactrequests SET reqtext = '{json_data['reqtext']}', "
                           f"updatedAt = '{cur_time}' WHERE id = {id}")
        db.session.commit()
        return {'message': "ContactRequest Updated!"}
    except Exception as e:
        db.session.rollback()
        return {'message': str(e)}


# Поиск аккаунта пользователя в БД
def login_user(form_data):
    # Получаем логин и пароль из данных формы
    username = form_data.get('loginField')
    password = form_data.get('passField')
    if username == '':
        return redirect(url_for('login'))
    # Ищем пользователя в БД
    result = db.session.execute(f"SELECT * FROM logins WHERE username = '{username}'").fetchone()
    # если пользователь не найден переадресуем на страницу /login
    if result is None:
        return redirect(url_for('login'))
    user = dict(result)
    # если пароль не прошел проверку, переадресуем на страницу /login
    if not bcrypt.checkpw(password.encode('utf-8'), user.get('password').encode('utf-8')):
        return redirect(url_for('login'))
    # иначе регистрируем сессию пользователя (записываем логин пользователя в параметр user) и высылаем cookie "AuthToken"
    else:
        response = redirect('/')
        session['user'] = user['username']
        session['userId'] = user['id']
        response.set_cookie('AuthToken', user['username'])
        return response


# Создание пользовательского аккаунта
def register_user(form_data):
    # Получаем данные пользователя из формы
    username = form_data.get('loginField')
    password = form_data.get('passField')
    email = form_data.get('emailField')
    # Проверяем полученные данные на наличие обязательных полей
    if username == '' or password == '' or email == '':
        return make_response(jsonify({'message': 'The data entered are not correct!'}), 400)
    # Создаем хеш пароля с солью
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    try:
        db.session.execute(f"INSERT INTO logins "
                           f"(username, password, email) "
                           f"VALUES ("
                           f"'{username}', "
                           f"'{hashed}', "
                           f"'{email}'"
                           ")")
        # Подтверждение изменений в БД
        db.session.commit()
        # Переадресуем на страницу авторизации
        return redirect(url_for('login'))
        # если возникла ошибка запроса в БД
    except Exception as e:
        # откатываем изменения в БД
        db.session.rollback()
        # возвращаем response с ошибкой сервера
        return make_response(jsonify({'message': str(e)}), 500)
