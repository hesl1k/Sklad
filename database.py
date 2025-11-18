import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

class Database:
    def __init__(self):
        self.connection = None
        
    def get_connection(self):
        """Создает новое соединение с MySQL"""
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**DB_CONFIG)
            return self.connection
        except Error as e:
            print(f"Ошибка подключения к БД: {e}")
            return None
            
    def disconnect(self):
        """Закрывает соединение"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            
    def execute_query(self, query, params=None, fetch=False):
        """Выполняет запрос с автоматическим управлением соединением"""
        connection = self.get_connection()
        if connection is None:
            print("ОШИБКА: Не удалось установить соединение с БД")
            return None
            
        try:
            cursor = connection.cursor(dictionary=True)
            print(f"Выполняем SQL: {query}")
            print(f"Параметры: {params}")
            
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
                print(f"Результат FETCH: {len(result)} записей")
            else:
                connection.commit()
                result = cursor.rowcount
                print(f"Результат EXECUTE: {result} строк")
                
            cursor.close()
            return result
        except Error as e:
            if connection:
                connection.rollback()
            print(f"ОШИБКА выполнения запроса: {e}")
            print(f"Запрос: {query}")
            print(f"Параметры: {params}")
            import traceback
            traceback.print_exc()
            return None

    # CRUD для товаров
    def get_tovars(self):
        """Получает все товары с информацией о категориях, складах и поставщиках"""
        query = """
        SELECT t.id_tov, t.kol, t.ob_ypak, t.ed_izm, t.cena, t.usl_hr, 
               t.srok_god, k.nazv as category_name, s.adres as sklad_adres,
               p.komp as postav_name
        FROM Tovar t
        JOIN Kateg k ON t.id_kat = k.id_kat
        JOIN Sklad s ON t.id_skl = s.id_skl
        JOIN Postav p ON t.id_post = p.id_post
        ORDER BY t.id_tov
        """
        return self.execute_query(query, fetch=True)
        
    def add_tovar(self, id_kat, kol, ob_ypak, ed_izm, cena, usl_hr, srok_god, id_skl, id_post):
        """Добавляет новый товар"""
        query = """
        INSERT INTO Tovar (id_kat, kol, ob_ypak, ed_izm, cena, usl_hr, srok_god, id_skl, id_post) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (id_kat, kol, ob_ypak, ed_izm, cena, usl_hr, srok_god, id_skl, id_post))
        
    def update_tovar(self, id_tov, id_kat, kol, ob_ypak, ed_izm, cena, usl_hr, srok_god, id_skl, id_post):
        """Обновляет товар"""
        query = """
        UPDATE Tovar 
        SET id_kat = %s, kol = %s, ob_ypak = %s, ed_izm = %s, cena = %s, 
            usl_hr = %s, srok_god = %s, id_skl = %s, id_post = %s
        WHERE id_tov = %s
        """
        return self.execute_query(query, (id_kat, kol, ob_ypak, ed_izm, cena, usl_hr, srok_god, id_skl, id_post, id_tov))
        
    def delete_tovar(self, id_tov):
        """Удаляет товар"""
        query = "DELETE FROM Tovar WHERE id_tov = %s"
        return self.execute_query(query, (id_tov,))

    # CRUD для категорий
    def get_kategs(self):
        """Получает все категории"""
        query = "SELECT * FROM Kateg ORDER BY id_kat"
        return self.execute_query(query, fetch=True)
        
    def add_kateg(self, nazv, opis):
        """Добавляет новую категорию"""
        query = "INSERT INTO Kateg (nazv, opis) VALUES (%s, %s)"
        return self.execute_query(query, (nazv, opis))
        
    def update_kateg(self, id_kat, nazv, opis):
        """Обновляет категорию"""
        query = "UPDATE Kateg SET nazv = %s, opis = %s WHERE id_kat = %s"
        return self.execute_query(query, (nazv, opis, id_kat))
        
    def delete_kateg(self, id_kat):
        """Удаляет категорию"""
        query = "DELETE FROM Kateg WHERE id_kat = %s"
        return self.execute_query(query, (id_kat,))

    # Вспомогательные методы для выпадающих списков
    def get_kategs_list(self):
        """Получает список категорий для выпадающего списка"""
        return self.get_kategs()
        
    def get_sklads_list(self):
        """Получает список складов для выпадающего списка"""
        query = "SELECT id_skl, adres FROM Sklad ORDER BY id_skl"
        return self.execute_query(query, fetch=True)
        
    def get_postavs_list(self):
        """Получает список поставщиков для выпадающего списка"""
        query = "SELECT id_post, komp FROM Postav ORDER BY id_post"
        return self.execute_query(query, fetch=True)

    # Аналитические запросы из вашей лабораторной работы
    def get_tovars_expiring_soon(self, days=30):
        """Товары с истекающим сроком годности"""
        query = """
        SELECT t.id_tov, k.nazv as category, t.srok_god,
               DATEDIFF(t.srok_god, CURDATE()) as days_until_expiry
        FROM Tovar t
        JOIN Kateg k ON t.id_kat = k.id_kat
        WHERE t.srok_god BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
        ORDER BY t.srok_god
        """
        return self.execute_query(query, (days,), fetch=True)
        
    def get_tovars_low_quantity(self, threshold=100):
        """Товары с низким количеством"""
        query = """
        SELECT t.id_tov, k.nazv as category, t.kol, s.adres as sklad
        FROM Tovar t
        JOIN Kateg k ON t.id_kat = k.id_kat
        JOIN Sklad s ON t.id_skl = s.id_skl
        WHERE t.kol < %s
        ORDER BY t.kol
        """
        return self.execute_query(query, (threshold,), fetch=True)
        
    def get_tovars_high_price(self, limit=10):
        """Самые дорогие товары"""
        query = """
        SELECT t.id_tov, k.nazv as category, t.cena, t.ed_izm
        FROM Tovar t
        JOIN Kateg k ON t.id_kat = k.id_kat
        ORDER BY t.cena DESC
        LIMIT %s
        """
        return self.execute_query(query, (limit,), fetch=True)
        
    def get_sales_by_category(self):
        """Анализ товаров по категориям"""
        query = """
        SELECT k.nazv as category, 
               COUNT(t.id_tov) as product_count,
               AVG(t.cena) as avg_price,
               SUM(t.kol) as total_quantity
        FROM Kateg k
        LEFT JOIN Tovar t ON k.id_kat = t.id_kat
        GROUP BY k.id_kat, k.nazv
        ORDER BY product_count DESC
        """
        return self.execute_query(query, fetch=True)

    # Статистика для главной страницы
    def get_tovars_count(self):
        query = "SELECT COUNT(*) as count FROM Tovar"
        result = self.execute_query(query, fetch=True)
        return result[0]['count'] if result else 0
        
    def get_kategs_count(self):
        query = "SELECT COUNT(*) as count FROM Kateg"
        result = self.execute_query(query, fetch=True)
        return result[0]['count'] if result else 0
        
    def get_sklads_count(self):
        query = "SELECT COUNT(*) as count FROM Sklad"
        result = self.execute_query(query, fetch=True)
        return result[0]['count'] if result else 0