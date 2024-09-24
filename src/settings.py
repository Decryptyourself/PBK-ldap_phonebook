# Настройки для подключения к PostgreSQL
DB_HOST = 'db'
DB_NAME = 'ldappbk_db'
DB_USER = 'ldappbk_db_user'
DB_PASSWORD = 'ldappbk_db_pass'
ADMIN_DB_USER = 'postgres'  # Суперпользователь PostgreSQL для создания базы и пользователя
ADMIN_DB_PASSWORD = 'postgres'  # Пароль суперпользователя PostgreSQL

# Настройки LDAP для подключения к Active Directory
AD_SERVER = 'your_IP_AD_server'
AD_DOMAIN = 'your_domain'
AD_USER = 'your_user'
AD_PASSWORD = 'your_password'
AD_PATH_OU = "OU=ALL,OU=Users,DC=local,DC=ru" # путь к OU пользователей
AD_TIME_SYNC = 30 # частота обновления данных из AD (в минутах)