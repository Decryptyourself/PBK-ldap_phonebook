# 📞 LDAP Phonebook PBK 📞

## Описание
**LDAP Phonebook PBK** — это простое веб-приложение для просмотра и поиска внутренних телефонных номеров пользователей из Active Directory (AD). Приложение использует Flask для веб-интерфейса и PostgreSQL для хранения данных. Данные извлекаются из AD через LDAPS-протокол с использованием библиотеки `ldap3`.

[![pbk-preview-update5.jpg](https://i.postimg.cc/xdXX2svx/pbk-preview-update5.jpg)](https://postimg.cc/gwPzyHB8)

---

## 📋 Функционал 📋
- Поиск сотрудников по фамилии, имени или внутреннему телефонному номеру.
- Отображение данных о сотрудниках, включая отдел, внутренний номер телефона, имя, должность, электронная почта, мобильный номер.
- Возможность перехода в почтовый клиент по умолчанию для отправки письма.
- Динамическая фильтрация по введённым данным.
- Автоматическая синхронизация данных из Active Directory.

### Необходимые поля для заполнения у пользователя в AD:
#### Вкладка Общие:
- Выводимое имя
- Эл.почта
#### Вкладка Телефоны:
- Домашний (используется как второй IP-телефон, если есть)
- Мобильный
- IP-телефон
#### Вкладка Организация:
- Должность
- Отдел (используется как внутренние отделы в Глобальных отделах)     
- Организация (используется как Глобальные отделы)

---

## 🛠️ Технологии 🛠️
- Python 3.9
- Flask
- PostgreSQL
- LDAPS (Active Directory)
- Docker & Docker Compose
- Nginx

---

## 🚀 Запуск приложения 🚀

### 1. Клонирование репозитория

```bash
git clone https://github.com/Decryptyourself/PBK-ldap_phonebook.git
```
```bash
cd PBK-ldap_phonebook
```
### 1.1. Установка Docker

#### обновление системы до актуального состояния
```bash
sudo apt update && sudo apt upgrade
```
#### установка пакетов, для работы apt по https
```bash
sudo apt install apt-transport-https ca-certificates curl software-properties-common
```
#### добавление ключа репозитория docker
```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```
#### добавление репозитория docker в систему
```bash
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
```
```bash
sudo apt update && apt-cache policy docker-ce
```
#### установка Docker
```bash
sudo apt install -y docker-ce
```
#### добавление текущего пользователя в группу docker, иначе при запуске docker будет ошибка подключения к сокету
```bash
sudo usermod -aG docker $(whoami)
```
#### проверка запуска docker
```bash
sudo systemctl status docker
```

### 1.1. Установка Docker Compose - утилита для управления контейнерами docker compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.25.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
```bash
sudo chmod +x /usr/local/bin/docker-compose
```

#### Установка зависимостей не требуется - Все необходимые зависимости уже включены в Docker-контейнер
```bash
sudo apt install python3-pip
```

#### ВАЖНО!
- Требуется установить сертификат AD на сервер, где будет работать приложение
- Без сертификата подключение к AD не будет установлено.
Копирование сертификата на сервер:
```powershell
scp -r C:\AD.cer admin@192.168.1.100:/home/admin/
```

#### для того чтобы система считала его доверенным, нужно скопировать его в папку:
```bash
sudo cp /home/admin/AD.crt /usr/local/share/ca-certificates/AD.crt
```
#### обновление сертификатов в системе
```bash
sudo update-ca-certificates
```

### 2. Конфигурация

Отредактируйте файл settings.py, указав необходимые параметры подключения к Active Directory:
- Настройки для подключения к PostgreSQL оставить по умолчанию
```python
# Настройки LDAP для подключения к Active Directory
AD_SERVER = 'your_IP_AD_server'
AD_DOMAIN = 'your_domain'
AD_USER = 'your_user'
AD_PASSWORD = 'your_password'
AD_PATH_OU = "OU=ALL,OU=Users,DC=local,DC=ru" # путь к OU пользователей
AD_TIME_SYNC = 30 # частота обновления данных из AD (в минутах)
```
Отредактируйте файл nginx/nginx.conf
Вместо localhost необходимо указать IP адрес сервера.

### 3. Запуск через Docker Compose

#### Приложение использует Docker Compose для работы с PostgreSQL, Nginx и Flask. Запуск:
```bash
sudo docker-compose build
```
```bash
sudo docker-compose up -d
```
```bash
sudo docker ps
```

Будут созданы и запущены следующие контейнеры:
1. app - Flask-приложение с Gunicorn
2. nginx - Nginx-сервер для проксирования запросов на Flask-приложение
3. db - PostgreSQL база данных для хранения данных о сотрудниках

#### После запуска приложение будет доступно на порту 80.


## ⚙️ Дополнительные команды ⚙️

#### Остановка всех контейнеров:
```bash
sudo docker-compose down
```
#### пересборка и запуск
```bash
sudo docker-compose up --build -d
```

#### Проверка логов:
```bash
sudo docker-compose logs -f
```

#### Перезапуск приложения:
```bash
sudo docker-compose restart
```

#### Удалить все контейнеры (!Если нет других! Удалить вообще все, что есть):
```bash
sudo docker stop $(docker ps -aq)
```
```bash
sudo docker rm $(docker ps -aq)
```
```bash
sudo docker system prune -a
```

## 🛡️ Настройка HTTPS с Nginx (опционально) 🛡️
Если вы хотите настроить HTTPS с использованием Let's Encrypt, необходимо настроить Nginx на работу с SSL-сертификатами.