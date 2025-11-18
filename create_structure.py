import os

# Структура папок и файлов
structure = {
    'app.py': '',
    'database.py': '',
    'config.py': '',
    'requirements.txt': 'Flask==2.3.3\nmysql-connector-python==8.1.0',
    'host.txt': 'main app - http://localhost:5001/',
    'static/css/style.css': '',
    'templates/base.html': '',
    'templates/index.html': '',
    'templates/tovars.html': '',
    'templates/add_tovar.html': '',
    'templates/edit_tovar.html': '',
    'templates/kategs.html': '',
    'templates/add_kateg.html': '',
    'templates/edit_kateg.html': '',
    'templates/analytics.html': '',
}

# Создание структуры
for file_path, content in structure.items():
    # Создаем папки если нужно
    dir_name = os.path.dirname(file_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
    
    # Создаем файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Структура проекта создана!")
