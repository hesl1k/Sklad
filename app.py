from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import Database

app = Flask(__name__)
app.secret_key = 'sklad_secret_key'
db = Database()

@app.route('/')
def index():
    """Главная страница"""
    try:
        tovars_count = db.get_tovars_count()
        kategs_count = db.get_kategs_count()
        sklads_count = db.get_sklads_count()
        
        return render_template('index.html',
                             tovars_count=tovars_count,
                             kategs_count=kategs_count,
                             sklads_count=sklads_count)
    except Exception as e:
        print(f"Ошибка при загрузке главной страницы: {e}")
        return render_template('index.html',
                             tovars_count=0,
                             kategs_count=0,
                             sklads_count=0)

# Маршруты для товаров
@app.route('/tovars')
def tovars():
    """Список всех товаров"""
    tovars_data = db.get_tovars()
    return render_template('tovars.html', tovars=tovars_data)

@app.route('/tovars/add', methods=['GET', 'POST'])
def add_tovar():
    """Добавление нового товара"""
    if request.method == 'POST':
        try:
            id_kat = int(request.form['id_kat'])
            kol = int(request.form['kol'])
            ob_ypak = float(request.form['ob_ypak'])
            ed_izm = request.form['ed_izm']
            cena = float(request.form['cena'])
            usl_hr = request.form['usl_hr']
            srok_god = request.form['srok_god']
            id_skl = int(request.form['id_skl'])
            id_post = int(request.form['id_post'])
            
            result = db.add_tovar(id_kat, kol, ob_ypak, ed_izm, cena, usl_hr, srok_god, id_skl, id_post)
            if result:
                flash('Товар успешно добавлен!', 'success')
                return redirect(url_for('tovars'))
            else:
                flash('Ошибка при добавлении товара', 'error')
        except Exception as e:
            flash(f'Ошибка при добавлении товара: {e}', 'error')
    
    # Получаем данные для выпадающих списков
    kategs = db.get_kategs_list()
    sklads = db.get_sklads_list()
    postavs = db.get_postavs_list()
    
    return render_template('add_tovar.html', 
                         kategs=kategs, 
                         sklads=sklads, 
                         postavs=postavs)

@app.route('/tovars/edit/<int:id_tov>', methods=['GET', 'POST'])
def edit_tovar(id_tov):
    """Редактирование товара"""
    if request.method == 'POST':
        try:
            id_kat = int(request.form['id_kat'])
            kol = int(request.form['kol'])
            ob_ypak = float(request.form['ob_ypak'])
            ed_izm = request.form['ed_izm']
            cena = float(request.form['cena'])
            usl_hr = request.form['usl_hr']
            srok_god = request.form['srok_god']
            id_skl = int(request.form['id_skl'])
            id_post = int(request.form['id_post'])
            
            result = db.update_tovar(id_tov, id_kat, kol, ob_ypak, ed_izm, cena, usl_hr, srok_god, id_skl, id_post)
            if result:
                flash('Товар успешно обновлен!', 'success')
                return redirect(url_for('tovars'))
            else:
                flash('Ошибка при обновлении товара', 'error')
        except Exception as e:
            flash(f'Ошибка при обновлении товара: {e}', 'error')
    
    # Получаем текущие данные товара
    tovars_data = db.get_tovars()
    tovar = next((t for t in tovars_data if t['id_tov'] == id_tov), None)
    
    if tovar is None:
        flash('Товар не найден', 'error')
        return redirect(url_for('tovars'))
    
    kategs = db.get_kategs_list()
    sklads = db.get_sklads_list()
    postavs = db.get_postavs_list()
    
    return render_template('edit_tovar.html', 
                         tovar=tovar, 
                         kategs=kategs, 
                         sklads=sklads, 
                         postavs=postavs)

@app.route('/tovars/delete/<int:id_tov>')
def delete_tovar(id_tov):
    """Удаление товара"""
    result = db.delete_tovar(id_tov)
    if result:
        flash('Товар успешно удален!', 'success')
    else:
        flash('Ошибка при удалении товара', 'error')
    
    return redirect(url_for('tovars'))

# Маршруты для категорий
@app.route('/kategs')
def kategs():
    """Список всех категорий"""
    kategs_data = db.get_kategs()
    return render_template('kategs.html', kategs=kategs_data)

@app.route('/kategs/add', methods=['GET', 'POST'])
def add_kateg():
    """Добавление новой категории"""
    if request.method == 'POST':
        try:
            nazv = request.form['nazv']
            opis = request.form['opis']
            
            result = db.add_kateg(nazv, opis)
            if result:
                flash('Категория успешно добавлена!', 'success')
                return redirect(url_for('kategs'))
            else:
                flash('Ошибка при добавлении категории', 'error')
        except Exception as e:
            flash(f'Ошибка при добавлении категории: {e}', 'error')
    
    return render_template('add_kateg.html')

@app.route('/kategs/edit/<int:id_kat>', methods=['GET', 'POST'])
def edit_kateg(id_kat):
    """Редактирование категории"""
    if request.method == 'POST':
        try:
            nazv = request.form['nazv']
            opis = request.form['opis']
            
            result = db.update_kateg(id_kat, nazv, opis)
            if result:
                flash('Категория успешно обновлена!', 'success')
                return redirect(url_for('kategs'))
            else:
                flash('Ошибка при обновлении категории', 'error')
        except Exception as e:
            flash(f'Ошибка при обновлении категории: {e}', 'error')
    
    kategs_data = db.get_kategs()
    kateg = next((k for k in kategs_data if k['id_kat'] == id_kat), None)
    
    if kateg is None:
        flash('Категория не найдена', 'error')
        return redirect(url_for('kategs'))
    
    return render_template('edit_kateg.html', kateg=kateg)

@app.route('/kategs/delete/<int:id_kat>')
def delete_kateg(id_kat):
    """Удаление категории"""
    result = db.delete_kateg(id_kat)
    if result:
        flash('Категория успешно удалена!', 'success')
    else:
        flash('Ошибка при удалении категории', 'error')
    
    return redirect(url_for('kategs'))

# Аналитика
@app.route('/analytics')
def analytics():
    """Страница аналитики"""
    return render_template('analytics.html')

# API для аналитических запросов
@app.route('/api/tovars_expiring_soon')
def api_tovars_expiring_soon():
    days = request.args.get('days', 30, type=int)
    data = db.get_tovars_expiring_soon(days)
    return jsonify(data)

@app.route('/api/tovars_low_quantity')
def api_tovars_low_quantity():
    threshold = request.args.get('threshold', 100, type=int)
    data = db.get_tovars_low_quantity(threshold)
    return jsonify(data)

@app.route('/api/tovars_high_price')
def api_tovars_high_price():
    limit = request.args.get('limit', 10, type=int)
    data = db.get_tovars_high_price(limit)
    return jsonify(data)

@app.route('/api/sales_by_category')
def api_sales_by_category():
    data = db.get_sales_by_category()
    return jsonify(data)

@app.teardown_appcontext
def close_connection(exception):
    """Закрывает соединение при завершении контекста приложения"""
    db.disconnect()

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Используем другой порт чтобы не конфликтовать