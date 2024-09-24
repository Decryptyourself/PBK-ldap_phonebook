// Главная функция для отображения шапок отделов при пустом поисковом запросе
function showStaticHeaders(departments) {
    var staticTablesDiv = document.getElementById('static-tables');
    staticTablesDiv.innerHTML = '';  // Очистка содержимого

    // Прохождение по отделам и создание шапки для каждого отдела
    for (var department in departments) {
        var departmentHeader = document.createElement('h2');
        departmentHeader.textContent = department;
        departmentHeader.classList.add('department-header');
        staticTablesDiv.appendChild(departmentHeader);

        // Создание таблицы с сотрудниками, но она скрыта по умолчанию
        var table = document.createElement('table');
        table.classList.add('department-table');
        table.style.display = 'none';

        var tbody = document.createElement('tbody');
        departments[department].forEach(function (user) {
            var row = document.createElement('tr');
            row.innerHTML = '<td>' + user.ip_phone + '</td>' + '<td>' + user.name + '</td>' + 
                            '<td>' + user.position + '</td>' + '<td>' + user.email + '</td>' +
                            '<td>' + user.mobile_phone + '</td>';
            tbody.appendChild(row);
        });

        table.appendChild(tbody);
        staticTablesDiv.appendChild(table);

        // Обработчик нажатия для показа/скрытия сотрудников
        departmentHeader.addEventListener('click', function () {
            var siblingTable = this.nextElementSibling;  // Таблица, следующая за заголовком

            // Проверка текущего состояние таблицы (показана или скрыта)
            if (siblingTable.style.display === 'none') {
                setTimeout(() => { siblingTable.style.display = 'table'; }, 3000); // Попытка сделать паузу (неудачно)
                //siblingTable.style.display = 'table';  // Показываем таблицу только для этого отдела
            } else {
                siblingTable.style.display = 'none';  // Скрытие таблицы
            }
        });
    }
}

// Функция для обработки поиска
function handleSearch(query, data) {
    var resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';  // Очистка результатов поиска

    var isNumeric = /^\d+$/.test(query);  // Проверка на цифры

    if (query && Object.keys(data).length > 0) {
        // Прохождение по отделам и создание таблицы для каждого отдела
        for (var department in data) {
            var employeesFound = false;
            var departmentHeader = document.createElement('h2');
            var table = document.createElement('table');
            var tbody = document.createElement('tbody');

            data[department].forEach(function (user) {
                var row = document.createElement('tr');
                
                // Поиск по номеру телефона (только цифры)
                if (isNumeric) {
                    var truncatedPhone = user.ip_phone.substring(0, query.length);
                    if (truncatedPhone === query) {
                        row.innerHTML = '<td class="column-ip-phone">' + user.ip_phone + '</td>' +
                                        '<td class="column-name">' + user.name + '</td>' +
                                        '<td class="column-position">' + user.position + '</td>' +
                                        '<td class="column-email"><a href="mailto:' + user.email + '">' + user.email + '</a></td>' +
                                        '<td class="column-mobile-phone">' + user.mobile_phone + '</td>';
                        tbody.appendChild(row);
                        employeesFound = true;
                    }
                // Поиск по имени (без учета регистра)
                } else {
                    var lowerCaseQuery = query.toLowerCase();
                    var lowerCaseName = user.name.toLowerCase();
                    if (lowerCaseName.includes(lowerCaseQuery)) {
                        row.innerHTML = '<td class="column-ip-phone">' + user.ip_phone + '</td>' +
                                        '<td class="column-name">' + user.name + '</td>' +
                                        '<td class="column-position">' + user.position + '</td>' +
                                        '<td class="column-email"><a href="mailto:' + user.email + '">' + user.email + '</a></td>' +
                                        '<td class="column-mobile-phone">' + user.mobile_phone + '</td>';
                        tbody.appendChild(row);
                        employeesFound = true;
                    }
                }
            });

            if (employeesFound) {
                departmentHeader.textContent = department;
                table.appendChild(tbody);
                resultsDiv.appendChild(departmentHeader);
                resultsDiv.appendChild(table);
            }
        }

        if (!resultsDiv.querySelector('table')) {
            var noResults = document.createElement('p');
            noResults.textContent = 'Не найдено';
            resultsDiv.appendChild(noResults);
        }
    } else {
        var noResults = document.createElement('p');
        noResults.textContent = 'Не найдено';
        resultsDiv.appendChild(noResults);
    }
}

// Основная функция обработки ввода в поле поиска
document.getElementById('search').addEventListener('input', function () {
    var query = this.value.trim();

    fetch('/search?query=' + encodeURIComponent(query))  // Кодировка запроса
        .then(response => response.json())
        .then(data => {
            var staticTablesDiv = document.getElementById('static-tables');
            var resultsDiv = document.getElementById('results');

            if (query) {
                resultsDiv.classList.remove('hidden');
                staticTablesDiv.classList.add('hidden');  // Скрываем статичные таблицы при поиске
                handleSearch(query, data);  // Выполняем поиск
            } else {
                resultsDiv.classList.add('hidden');
                staticTablesDiv.classList.remove('hidden');  // Показываем статичные таблицы при очистке поиска
                showStaticHeaders(data);  // Если поиска нет, показываем шапки отделов
            }
        });
});// Основная функция обработки ввода в поле поиска

// Обработчик событий на все заголовки отделов
document.querySelectorAll('.department-header').forEach(function (departmentHeader) {
    departmentHeader.addEventListener('click', function () {
        var siblingTable = this.nextElementSibling;  // Таблица, следующая за заголовком

        // Проверка текущего состояние таблицы (показана или скрыта)
        if (siblingTable.style.display === 'none' || siblingTable.style.display === '') {
            siblingTable.style.display = 'table';  // Показываем таблицу только для этого отдела
        } else {
            siblingTable.style.display = 'none';  // Скрываем таблицу
        }
    });
});

// Функция для отображения статичных заголовков отделов при первой загрузке страницы
function showStaticHeaders(data) {
    var staticTablesDiv = document.getElementById('static-tables');
    var resultsDiv = document.getElementById('results');

    resultsDiv.classList.add('hidden');  // Скрытие результатов поиска
    staticTablesDiv.classList.remove('hidden');  // Показ статичных таблиц

    // Отображение заголовков отделов
    data.forEach(function(department) {
        var header = document.createElement('h2');
        header.className = 'department-header';
        header.textContent = department.name;  //имя отдела
        staticTablesDiv.appendChild(header);

        // Таблица для отдела (по умолчанию скрыта)
        var table = document.createElement('table');
        table.style.display = 'none';  // Скрыта по умолчанию
        staticTablesDiv.appendChild(table);
    });

// Итог: после создания всех заголовков добавление к ним обработчика кликов (fix, иначе не работает)
document.querySelectorAll('.department-header').forEach(function (departmentHeader) {
    departmentHeader.addEventListener('click', function () {
        var siblingTable = this.nextElementSibling;  // Таблица, следующая за заголовком
        // Проверка текущего состояния таблицы (показана или скрыта)
        if (siblingTable.style.display === 'none' || siblingTable.style.display === '') {
            setTimeout(() => { siblingTable.style.display = 'table'; }, 3000); // Попытка сделать паузу (неудачно)
            //siblingTable.style.display = 'table';  // Показываем таблицу только для этого отдела
        } else {
            siblingTable.style.display = 'none';  // Скрытие таблицы
        }
    });
});
}