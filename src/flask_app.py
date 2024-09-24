from flask import Flask, render_template, request, jsonify
import psycopg2
from settings import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('query', '')
    query = query.lower() # Приведение запроса к нижнему регистру
    departments = get_employees_by_department(query)
    return jsonify(departments) # Возврат данных в JSON для клиента

# Запрос из БД по отделам
def get_employees_by_department(query=None):
    connection = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = connection.cursor()

    # Если запрос передан --> поиск по имени или внутреннему номеру телефона
    if query:
        cursor.execute("""
            SELECT ip_phone, name, department, position, email, mobile_phone
            FROM users
            WHERE LOWER(name) LIKE %s OR ip_phone LIKE %s
            ORDER BY department, ip_phone;
        """, (f'%{query}%', f'%{query}%'))
    else:
        cursor.execute("""
            SELECT ip_phone, name, department, position, email, mobile_phone
            FROM users
            ORDER BY department, ip_phone;
        """)
    employees = cursor.fetchall()
    
    departments = {}
    for employee in employees:
        ip_phone, name, department, position, email, mobile_phone = employee
        if department not in departments:
            departments[department] = []
        departments[department].append({
            'ip_phone': ip_phone,
            'name': name,
            'position': position,
            'email': email,
            'mobile_phone': mobile_phone
        })
    cursor.close()
    connection.close()    
    return departments

# Путь для отображения главной страницы
@app.route('/')
def index():
    departments = get_employees_by_department()
    return render_template('index.html', departments=departments)

# ДЛЯ ТЕСТОВ, БЕЗ WSGI
if __name__ == "__main__":
    app.run()