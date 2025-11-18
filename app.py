from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime, date
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Инициализация MySQL
mysql = MySQL(app)

@app.route('/')
def index():
    """Главная страница"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    # Получаем статистику для дашборда
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Общее количество товаров
    cursor.execute("SELECT COUNT(*) as total FROM Tovar")
    total_products = cursor.fetchone()['total']
    
    # Общее количество категорий
    cursor.execute("SELECT COUNT(*) as total FROM Kateg")
    total_categories = cursor.fetchone()['total']
    
    # Общая стоимость товаров
    cursor.execute("SELECT SUM(kol * cena) as total FROM Tovar")
    total_value_result = cursor.fetchone()
    total_value = total_value_result['total'] if total_value_result['total'] else 0
    
    # Товары с истекающим сроком годности
    cursor.execute("""
        SELECT t.id_tov, k.nazv as category, t.kol, t.cena, t.srok_god, 
               DATEDIFF(t.srok_god, CURDATE()) as days_left,
               s.adres as warehouse
        FROM Tovar t
        JOIN Kateg k ON t.id_kat = k.id_kat
        JOIN Sklad s ON t.id_skl = s.id_skl
        WHERE t.srok_god BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
        ORDER BY t.srok_god ASC
        LIMIT 10
    """)
    expiring_products = cursor.fetchall()
    
    cursor.close()
    
    return render_template('index.html',
                         total_products=total_products,
                         total_categories=total_categories,
                         total_value=total_value,
                         expiring_products=expiring_products)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль!', 'danger')
    
    return render_template('auth/login.html')

@app.route('/register/', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        if account:
            flash('Аккаунт уже существует!', 'danger')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Неверный email адрес!', 'danger')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Имя пользователя должно содержать только символы и цифры!', 'danger')
        elif not username or not password or not email:
            flash('Пожалуйста, заполните все поля!', 'danger')
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email))
            mysql.connection.commit()
            flash('Вы успешно зарегистрировались!', 'success')
            return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    """Выход из системы"""
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# Products routes
@app.route('/products')
def products():
    """Страница товаров"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Получаем товары с информацией о категориях и складах
    cursor.execute("""
        SELECT t.*, k.nazv as category_name, s.adres as warehouse_address, p.komp as supplier_name
        FROM Tovar t
        JOIN Kateg k ON t.id_kat = k.id_kat
        JOIN Sklad s ON t.id_skl = s.id_skl
        JOIN Postav p ON t.id_post = p.id_post
        ORDER BY t.id_tov
    """)
    products = cursor.fetchall()
    
    # Получаем категории для фильтров
    cursor.execute("SELECT * FROM Kateg")
    categories = cursor.fetchall()
    
    # Получаем склады для фильтров
    cursor.execute("SELECT * FROM Sklad")
    warehouses = cursor.fetchall()
    
    cursor.close()
    
    return render_template('products.html', 
                         products=products, 
                         categories=categories,
                         warehouses=warehouses)

@app.route('/products/add', methods=['POST'])
def add_product():
    """Добавление товара"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            id_kat = request.form['category_id']
            kol = request.form['quantity']
            ob_ypak = request.form['package_volume']
            ed_izm = request.form['unit']
            cena = request.form['price']
            usl_hr = request.form.get('storage_conditions', '')
            srok_god = request.form['expiry_date']
            id_skl = request.form['warehouse_id']
            id_post = request.form['supplier_id']
            
            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO Tovar (id_kat, kol, ob_ypak, ed_izm, cena, usl_hr, srok_god, id_skl, id_post)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (id_kat, kol, ob_ypak, ed_izm, cena, usl_hr, srok_god, id_skl, id_post))
            
            mysql.connection.commit()
            cursor.close()
            
            flash('Товар успешно добавлен!', 'success')
            
        except Exception as e:
            flash(f'Ошибка при добавлении товара: {str(e)}', 'danger')
    
    return redirect(url_for('products'))

@app.route('/products/update/<int:product_id>', methods=['POST'])
def update_product(product_id):
    """Обновление товара"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            id_kat = request.form['category_id']
            kol = request.form['quantity']
            ob_ypak = request.form['package_volume']
            ed_izm = request.form['unit']
            cena = request.form['price']
            usl_hr = request.form.get('storage_conditions', '')
            srok_god = request.form['expiry_date']
            id_skl = request.form['warehouse_id']
            id_post = request.form['supplier_id']
            
            cursor = mysql.connection.cursor()
            cursor.execute("""
                UPDATE Tovar 
                SET id_kat = %s, kol = %s, ob_ypak = %s, ed_izm = %s, cena = %s, 
                    usl_hr = %s, srok_god = %s, id_skl = %s, id_post = %s
                WHERE id_tov = %s
            """, (id_kat, kol, ob_ypak, ed_izm, cena, usl_hr, srok_god, id_skl, id_post, product_id))
            
            mysql.connection.commit()
            cursor.close()
            
            flash('Товар успешно обновлен!', 'success')
            
        except Exception as e:
            flash(f'Ошибка при обновлении товара: {str(e)}', 'danger')
    
    return redirect(url_for('products'))

@app.route('/products/delete/<int:product_id>')
def delete_product(product_id):
    """Удаление товара"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Tovar WHERE id_tov = %s", (product_id,))
        mysql.connection.commit()
        cursor.close()
        
        flash('Товар успешно удален!', 'success')
        
    except Exception as e:
        flash(f'Ошибка при удалении товара: {str(e)}', 'danger')
    
    return redirect(url_for('products'))

# Categories routes
@app.route('/categories')
def categories():
    """Страница категорий"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Kateg ORDER BY nazv")
    categories = cursor.fetchall()
    cursor.close()
    
    return render_template('categories.html', categories=categories)

@app.route('/categories/add', methods=['POST'])
def add_category():
    """Добавление категории"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            nazv = request.form['name']
            opis = request.form.get('description', '')
            
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO Kateg (nazv, opis) VALUES (%s, %s)", (nazv, opis))
            mysql.connection.commit()
            cursor.close()
            
            flash('Категория успешно добавлена!', 'success')
            
        except Exception as e:
            flash(f'Ошибка при добавлении категории: {str(e)}', 'danger')
    
    return redirect(url_for('categories'))

@app.route('/categories/update/<int:category_id>', methods=['POST'])
def update_category(category_id):
    """Обновление категории"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            nazv = request.form['name']
            opis = request.form.get('description', '')
            
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE Kateg SET nazv = %s, opis = %s WHERE id_kat = %s", 
                          (nazv, opis, category_id))
            mysql.connection.commit()
            cursor.close()
            
            flash('Категория успешно обновлена!', 'success')
            
        except Exception as e:
            flash(f'Ошибка при обновлении категории: {str(e)}', 'danger')
    
    return redirect(url_for('categories'))

@app.route('/categories/delete/<int:category_id>')
def delete_category(category_id):
    """Удаление категории"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Kateg WHERE id_kat = %s", (category_id,))
        mysql.connection.commit()
        cursor.close()
        
        flash('Категория успешно удалена!', 'success')
        
    except Exception as e:
        flash(f'Ошибка при удалении категории: {str(e)}', 'danger')
    
    return redirect(url_for('categories'))

# Analytics routes
@app.route('/analytics')
def analytics():
    """Страница аналитики"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Статистика по складам
    cursor.execute("""
        SELECT s.adres, COUNT(t.id_tov) as product_count, 
               SUM(t.kol) as total_quantity, SUM(t.kol * t.cena) as total_value
        FROM Sklad s
        LEFT JOIN Tovar t ON s.id_skl = t.id_skl
        GROUP BY s.id_skl, s.adres
        ORDER BY total_value DESC
    """)
    warehouse_stats = cursor.fetchall()
    
    # Статистика по категориям
    cursor.execute("""
        SELECT k.nazv, COUNT(t.id_tov) as product_count, 
               SUM(t.kol) as total_quantity, SUM(t.kol * t.cena) as total_value
        FROM Kateg k
        LEFT JOIN Tovar t ON k.id_kat = t.id_kat
        GROUP BY k.id_kat, k.nazv
        ORDER BY total_value DESC
    """)
    category_stats = cursor.fetchall()
    
    # Товары с истекающим сроком годности
    cursor.execute("""
        SELECT t.id_tov, k.nazv as category, t.kol, t.cena, t.srok_god, 
               DATEDIFF(t.srok_god, CURDATE()) as days_left,
               s.adres as warehouse, p.komp as supplier
        FROM Tovar t
        JOIN Kateg k ON t.id_kat = k.id_kat
        JOIN Sklad s ON t.id_skl = s.id_skl
        JOIN Postav p ON t.id_post = p.id_post
        WHERE t.srok_god BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
        ORDER BY t.srok_god ASC
    """)
    expiring_products = cursor.fetchall()
    
    cursor.close()
    
    return render_template('analytics.html',
                         warehouse_stats=warehouse_stats,
                         category_stats=category_stats,
                         expiring_products=expiring_products)

# API endpoints
@app.route('/api/suppliers')
def api_suppliers():
    """API для получения поставщиков"""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id_post, komp FROM Postav ORDER BY komp")
    suppliers = cursor.fetchall()
    cursor.close()
    
    return jsonify(suppliers)

@app.route('/api/warehouses')
def api_warehouses():
    """API для получения складов"""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id_skl, adres FROM Sklad ORDER BY adres")
    warehouses = cursor.fetchall()
    cursor.close()
    
    return jsonify(warehouses)

if __name__ == '__main__':
    app.run(debug=True)