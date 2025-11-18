from flask_mysqldb import MySQL
from config import Config

def init_models(app):
    """Инициализация моделей"""
    app.config['MYSQL_HOST'] = Config.MYSQL_HOST
    app.config['MYSQL_USER'] = Config.MYSQL_USER
    app.config['MYSQL_PASSWORD'] = Config.MYSQL_PASSWORD
    app.config['MYSQL_DB'] = Config.MYSQL_DB
    app.config['MYSQL_PORT'] = Config.MYSQL_PORT
    app.config['MYSQL_CURSORCLASS'] = Config.MYSQL_CURSORCLASS
    
    return MySQL(app)

class Product:
    @staticmethod
    def get_all(mysql):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT t.*, k.nazv as category_name, s.adres as warehouse_address 
            FROM Tovar t
            JOIN Kateg k ON t.id_kat = k.id_kat
            JOIN Sklad s ON t.id_skl = s.id_skl
        """)
        products = cursor.fetchall()
        cursor.close()
        return products

class Category:
    @staticmethod
    def get_all(mysql):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Kateg")
        categories = cursor.fetchall()
        cursor.close()
        return categories