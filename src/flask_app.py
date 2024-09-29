from flask import Flask, render_template, request, jsonify
import psycopg2
from settings import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('query', '').lower()  # Приведение запроса к нижнему регистру
    data = get_employees_by_global_department_with_query(query)
    return jsonify(data)  # Возврат данных в JSON для клиента

# Получение данных по департаментам и отделам
def get_employees_by_global_department_with_query(query=None):
    connection = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = connection.cursor()

    sql_query = """
        SELECT global_department, department, ip_phone, ip_phone_second, name, position, email, mobile_phone
        FROM users
    """

    params = []

    if query:
        sql_query += " WHERE LOWER(name) LIKE %s OR ip_phone LIKE %s"
        params.extend([f'%{query}%', f'%{query}%'])

    sql_query += " ORDER BY global_department, department;"

    cursor.execute(sql_query, params)
    employees = cursor.fetchall()

    data = {}
    for employee in employees:
        global_department, department, ip_phone, ip_phone_second, name, position, email, mobile_phone = employee
        if global_department not in data:
            data[global_department] = {}
        if department not in data[global_department]:
            data[global_department][department] = []
        data[global_department][department].append({
            'ip_phone': ip_phone,
            'ip_phone_second': ip_phone_second,
            'name': name,
            'position': position,
            'email': email,
            'mobile_phone': mobile_phone
        })

    # Применяем сортировку внутри каждого отдела
    for global_department in data:
        for department in data[global_department]:
            data[global_department][department] = sort_employees(data[global_department][department])

    cursor.close()
    connection.close()
    return data

# Запрос из БД по департаментам
def get_employees_by_global_department():
    connection = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = connection.cursor()

    cursor.execute("""
        SELECT DISTINCT global_department
        FROM users
        ORDER BY global_department;
    """)
    global_depts = cursor.fetchall()

    global_departments = [global_dept_tuple[0] for global_dept_tuple in global_depts]

    cursor.close()
    connection.close()
    return global_departments

# Получение сотрудников по отделам с возможностью фильтрации по департаменту
def get_employees_by_department(query=None, global_department=None):
    connection = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = connection.cursor()

    sql_query = """
        SELECT ip_phone, ip_phone_second, name, department, position, email, mobile_phone
        FROM users
    """

    params = []
    conditions = []

    if global_department:
        conditions.append("global_department = %s")
        params.append(global_department)

    if query:
        conditions.append("(LOWER(name) LIKE %s OR ip_phone LIKE %s)")
        params.extend([f'%{query}%', f'%{query}%'])

    if conditions:
        sql_query += " WHERE " + " AND ".join(conditions)

    sql_query += " ORDER BY department;"

    cursor.execute(sql_query, params)
    employees = cursor.fetchall()

    departments = {}
    for employee in employees:
        ip_phone, ip_phone_second, name, department, position, email, mobile_phone = employee
        if department not in departments:
            departments[department] = []
        departments[department].append({
            'ip_phone': ip_phone,
            'ip_phone_second': ip_phone_second,
            'name': name,
            'position': position,
            'email': email,
            'mobile_phone': mobile_phone
        })

    # Сортировка внутри каждого отдела
    for department in departments:
        departments[department] = sort_employees(departments[department])

    cursor.close()
    connection.close()
    return departments

def sort_employees(employees):
    # Сортировка сотрудников внутри отдела
    def sort_key(employee):
        position = employee['position'].lower()
        if 'руководитель' in position and 'заместитель' not in position:
            return (0, 0)  # Руководитель - первый
        elif 'заместитель руководителя' in position:
            return (1, 0)  # Заместитель руководителя - второй
        else:
            # Преобразование ip_phone в число для корректной сортировки
            try:
                ip_phone = int(employee['ip_phone'])
            except ValueError:
                ip_phone = float('inf')  # Если не число, то в конец
            return (2, ip_phone)  # Остальные сортируются по внутреннему номеру
    # Сортировка списка сотрудников по ключу
    return sorted(employees, key=sort_key)

@app.route('/get_global_departments')
def get_global_departments():
    global_departments = get_employees_by_global_department()
    return jsonify(global_departments)

@app.route('/get_departments')
def get_departments():
    global_department = request.args.get('global_department', '')
    departments = get_employees_by_department(global_department=global_department)
    return jsonify(departments)

@app.route('/')
def index():
    global_departments = get_employees_by_global_department()
    departments = get_employees_by_department()
    print(global_departments)
    print(departments)
    return render_template('index.html', departments=departments, global_departments=global_departments)

# ДЛЯ ТЕСТОВ, БЕЗ WSGI
if __name__ == "__main__":
    app.run()