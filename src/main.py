import ssl
import time
import schedule
import psycopg2
from ldap3 import Server, Connection, ALL, NTLM, SUBTREE, Tls
from settings import *

# Проверка на существования БД ldappbk_db (проверка на первый запуск)
def check_database_exists():
    connection = psycopg2.connect(
        host=DB_HOST,
        dbname='postgres',  # Подключение к БД, по умолчанию postgres
        user=ADMIN_DB_USER,
        password=ADMIN_DB_PASSWORD
    )
    connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
    exists = cursor.fetchone()
    cursor.close()
    connection.close()
    return exists is not None

# TODO: Сделать проверку на пользователя без БД,
# иначе у пользователя не будет прав на созданную базу
# Cоздание новой БД для phonebook
def create_database():
    connection = psycopg2.connect(
        host=DB_HOST,
        dbname='postgres',
        user=ADMIN_DB_USER,
        password=ADMIN_DB_PASSWORD
    )
    connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE {DB_NAME}")
    cursor.close()
    connection.close()

# Проверка на существования пользователя ldappbk_db_user
# (на случай если был удален, а база осталась)
def check_user_exists():
    connection = psycopg2.connect(
        host=DB_HOST,
        dbname='postgres',
        user=ADMIN_DB_USER,
        password=ADMIN_DB_PASSWORD
    )
    connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute(f"SELECT 1 FROM pg_roles WHERE rolname = '{DB_USER}'")
    exists = cursor.fetchone()
    cursor.close()
    connection.close()
    return exists is not None

# Создание пользователя БД для ldappbk_db
def create_user():
    connection = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,  # Подключаемся к созданной базе данных ldappbk_db
        user=ADMIN_DB_USER,  # Администратор базы данных
        password=ADMIN_DB_PASSWORD
    )
    connection.autocommit = True
    cursor = connection.cursor()
    
    # Создание пользователя
    cursor.execute(f"CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}'")    
    # Предоставление привилегий на базу данных
    cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER}")    
    # Передача прав владения схемой public в базе ldappbk_db новому пользователю
    cursor.execute(f"ALTER SCHEMA public OWNER TO {DB_USER}")    
    # Предоставление всех привилегий на схему public в базе ldappbk_db
    cursor.execute(f"GRANT ALL PRIVILEGES ON SCHEMA public TO {DB_USER}")
    
    cursor.close()
    connection.close()

# Создание БД и пользователя, если их нет (первый запуск)
def setup_database_and_user():
    if not check_database_exists():
        create_database() # Если БД не найдена, создание
    if not check_user_exists():
        create_user() # Если пользователь БД не найден, создание

# Создание таблицы, если ее нет
def create_tables():
    connection = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        ip_phone VARCHAR(20),
        ip_phone_second VARCHAR(20),
        name VARCHAR(150),
        position VARCHAR(255),
        department VARCHAR(255),
        global_department VARCHAR(255),
        email VARCHAR(150),
        mobile_phone VARCHAR(255),
        login VARCHAR(100),
        description VARCHAR(255),
        room VARCHAR(255)
    );
    """)

    # Проверка на наличие добавляемого ip_phone
    cursor.execute("""
    SELECT 1 FROM pg_constraint
    WHERE conname = 'unique_ip_phone' AND conrelid = 'users'::regclass;
    """)

    # Если добавляемый ip_phone не найден, то добавление его в таблицу
    if cursor.fetchone() is None:
        cursor.execute("""
        ALTER TABLE users
        ADD CONSTRAINT unique_ip_phone UNIQUE (ip_phone);
        """)

    connection.commit()
    cursor.close()
    connection.close()

# Внесения данных в БД
def store_user_data_in_db(users):
    connection = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = connection.cursor()

    for user in users:
        # Если ip_phone = '-', удалить запись с таким name
        if user['ip_phone'] == '-':
            cursor.execute("""
            DELETE FROM users WHERE name = %s
            """, (user['name'],))
            continue

        # Если запись с таким же ip_phone существует, то обновление остальных полей
        cursor.execute("""
        SELECT name FROM users WHERE ip_phone = %s
        """, (user['ip_phone'],))
        existing_record = cursor.fetchone()

        if existing_record:
            # Если найден ip_phone, то обновление остальных полей
            cursor.execute("""
            UPDATE users SET ip_phone_second = %s, name = %s, position = %s, department = %s,
                            global_department = %s, email = %s, mobile_phone = %s, login = %s,
                            description = %s, room = %s WHERE ip_phone = %s
            """, (user['ip_phone_second'], user['name'], user['position'], user['department'],
                    user['global_department'], user['email'], user['mobile_phone'], user['login'],
                    user['description'], user['room'], user['ip_phone']))
        else:
            # Если ip_phone не найден, добавление новой записи
            cursor.execute("""
            INSERT INTO users (ip_phone, ip_phone_second, name, position, department, global_department,
                                email, mobile_phone, login, description, room) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user['ip_phone'], user['ip_phone_second'], user['name'], user['position'],
                    user['department'], user['global_department'], user['email'],
                    user['mobile_phone'], user['login'], user['description'], user['room']))

        # Очистка записи с таким же name, но с другим ip_phone
        cursor.execute("""
        DELETE FROM users WHERE name = %s AND ip_phone != %s
        """, (user['name'], user['ip_phone']))

    connection.commit()
    cursor.close()
    connection.close()

# Получение данных из Active Directory
def get_ad_users():
    tls_configuration = Tls(version=ssl.PROTOCOL_TLSv1_2)
    server = Server(AD_SERVER, port=636, use_ssl=True, get_info=ALL, tls=tls_configuration)
    # Установка соединения c AD
    connection = Connection(
        server,
        user=f"{AD_DOMAIN}\\{AD_USER}",
        password=AD_PASSWORD,
        authentication=NTLM,
        auto_bind='DEFAULT'
    )
    # прохождение аутентификации
    connection.bind()

    search_filter = '(objectClass=person)'
    # Именования аттрибутов, для удобства
    attr_IpPhoneUser = 'ipPhone' # ipPhone - Телефоны/IP-телефон
    attr_SecondIpPhoneUser = 'homePhone' # homePhone - Телефоны/Домашний
    attr_DisplayNameUser = 'displayName' # displayName - Общие/Выводимое имя
    attr_PositionUser = 'title' # title - Организация/Должность
    attr_DepartmentUser = 'department' # department - Организация/Отдел (Внутренние отделы)     
    attr_GlobalDepartmentUser = 'company' # company - Организация/Организация (Глобальные отделы)
    attr_EmailUser = 'mail' # mail - Общие/Эл.почта
    attr_MobilePhoneUser = 'mobile' # mobile - Телефоны/Мобильный
    # Незайдествованные атрибуты на фронте
    attr_LoginUser = 'userPrincipalName' # userPrincipalName - Учетная запись/Имя входа пользователя
    attr_DescriptionUser = 'description' # description - Общие/Описание
    attr_RoomUser = 'physicalDeliveryOfficeName' # physicalDeliveryOfficeName - Общие/Комната

    attributes = [attr_IpPhoneUser, attr_SecondIpPhoneUser, attr_DisplayNameUser, attr_PositionUser,
                attr_DepartmentUser, attr_GlobalDepartmentUser, attr_EmailUser, attr_MobilePhoneUser,
                attr_LoginUser, attr_DescriptionUser, attr_RoomUser
                ]

    result = connection.search(AD_PATH_OU, search_filter, search_scope=SUBTREE, attributes=attributes)
    if not result:
        return []

    users = []
    for attributeValue in connection.entries:
        user_data = {
            'ip_phone': attributeValue.ipPhone.value if attributeValue.ipPhone else '-',
            'ip_phone_second': attributeValue.homePhone.value if attributeValue.homePhone else '-',
            'name': attributeValue.displayName.value,
            'position': attributeValue.title.value if attributeValue.title else '-',
            'department': attributeValue.department.value if attributeValue.department else 'Отдел не указан',
            'global_department': attributeValue.company.value if attributeValue.company else '-',
            'email': attributeValue.mail.value if attributeValue.mail else '-',
            'mobile_phone': attributeValue.mobile.value if attributeValue.mobile else '-',
            'login': attributeValue.userPrincipalName.value,
            'description': attributeValue.description.value if attributeValue.description else '-',
            'room': attributeValue.physicalDeliveryOfficeName.value if attributeValue.physicalDeliveryOfficeName else '-'
        }
        users.append(user_data)

    store_user_data_in_db(users)
    return users

# Планировщик для обновления данных из AD
def schedule_update():
    get_ad_users()

# Основная функция для планирования задач
def main():
    setup_database_and_user()  # Проверка и создание БД и пользователя, если их нет
    create_tables()  # Создание таблицы, если ее нет
    schedule_update()  # Обновление данных

    # Задача планировщику на обновление данных из AD (в минутах)
    schedule.every(AD_TIME_SYNC).minutes.do(schedule_update)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()