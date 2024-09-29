// Функция инициализации обработчиков событий на заголовки департаментов
function initializeGlobalDepartmentHeaders() {
    document.querySelectorAll('.global-department-header').forEach(function (deptHeader) {
        deptHeader.addEventListener('click', function () {
            var searchField = document.getElementById('search').value.trim();
            if (searchField === '') {  // Проверяем, что поле поиска пустое
                var globalDepartment = this.textContent.trim();

                fetch('/get_departments?global_department=' + encodeURIComponent(globalDepartment))
                    .then(response => response.json())
                    .then(departments => {
                        showDepartments(departments);
                    });
            }
        });
    });
}

// Функция инициализации обработчиков событий на заголовки отделов
function initializeDepartmentHeaders() {
    document.querySelectorAll('.department-header').forEach(function (departmentHeader) {
        departmentHeader.addEventListener('click', function () {
            var siblingTable = this.nextElementSibling;

            if (siblingTable.style.display === 'none' || siblingTable.style.display === '') {
                siblingTable.style.display = 'table';
            } else {
                siblingTable.style.display = 'none';
            }
        });
    });
}

function loadGlobalDepartments() {
    fetch('/get_global_departments')
        .then(response => response.json())
        .then(global_departments => {
            var globalStaticTablesDiv = document.getElementById('global-static-tables');
            globalStaticTablesDiv.innerHTML = '';

            global_departments.forEach(function(global_department, index) {
                var global_departmentTable = document.createElement('div');
                global_departmentTable.classList.add('global-department-table');

                var global_departmentHeader = document.createElement('h2');
                global_departmentHeader.textContent = global_department;
                global_departmentHeader.classList.add('global-department-header');
                global_departmentHeader.id = 'global-department-header-' + (index + 1);
                global_departmentTable.appendChild(global_departmentHeader);

                globalStaticTablesDiv.appendChild(global_departmentTable);
            });

            enableGlobalDepartmentClicks();  // Активация кликов по департаментам
        });
}

function showDepartments(departments) {
    var staticTablesDiv = document.getElementById('static-tables');
    staticTablesDiv.innerHTML = '';  // Очистка правого блока

    for (var department in departments) {
        var departmentHeader = document.createElement('h3');
        departmentHeader.textContent = department;
        departmentHeader.classList.add('department-header');
        staticTablesDiv.appendChild(departmentHeader);

        var table = document.createElement('table');
        table.classList.add('department-table');
        table.style.display = 'none';  // Таблицы скрыты по умолчанию

        var tbody = document.createElement('tbody');

        departments[department].forEach(function (user) {
            var row = document.createElement('tr');
            row.innerHTML = '<td>' + user.ip_phone + '</td>' +
                            '<td>' + user.name + '</td>' +
                            '<td>' + user.position + '</td>' +
                            '<td><a href="mailto:' + user.email + '">' + user.email + '</a></td>' +
                            '<td>' + user.mobile_phone + '</td>';
            tbody.appendChild(row);
        });

        table.appendChild(tbody);
        staticTablesDiv.appendChild(table);
    }

    initializeDepartmentHeaders(); // Инициализация обработчика на заголовки отделов
}

// Функция отображения статичных заголовков отделов при первой загрузке страницы
function showStaticHeaders(departments, global_departments) {
    var staticTablesDiv = document.getElementById('static-tables');
    var globalStaticTablesDiv = document.getElementById('global-static-tables');
    staticTablesDiv.innerHTML = '';  // Очистка содержимого
    globalStaticTablesDiv.innerHTML = '';  // Очистка содержимого для глобальных департаментов

    // Прохождение по глобальным департаментам и создание шапки для каждого
    global_departments.forEach(function(global_department, index) {
        // Создание контейнера для каждого департамента
        var global_departmentTable = document.createElement('div');
        global_departmentTable.classList.add('global-department-table');
        
        // Создание заголовка для глобального департамента
        var global_departmentHeader = document.createElement('h2');
        global_departmentHeader.textContent = global_department;
        global_departmentHeader.classList.add('global-department-header');
        global_departmentHeader.id = 'global-department-header-' + (index + 1);  // Уникальный ID
        global_departmentTable.appendChild(global_departmentHeader);
        
        // Добавление заголовка глобального департамента в контейнер для глобальных департаментов
        globalStaticTablesDiv.appendChild(global_departmentTable);
    });

    // Прохождение по отделам и создание шапки для каждого отдела
    for (var department in departments) {
        var departmentHeader = document.createElement('h3');
        departmentHeader.textContent = department;
        departmentHeader.classList.add('department-header');
        staticTablesDiv.appendChild(departmentHeader);

        // Создание таблицы с сотрудниками (скрыта по умолчанию)
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
    }

    // Инициализация обработчиков событий на заголовки отделов
    initializeDepartmentHeaders();
}

function disableGlobalDepartmentClicks() {
    document.querySelectorAll('.global-department-header').forEach(function (deptHeader) {
        var newDeptHeader = deptHeader.cloneNode(true);
        deptHeader.parentNode.replaceChild(newDeptHeader, deptHeader);
    });
}

function enableGlobalDepartmentClicks() {
    initializeGlobalDepartmentHeaders();
}

// Функция обработки поиска
function handleSearch(query, data) {
    var staticTablesDiv = document.getElementById('static-tables');
    staticTablesDiv.innerHTML = '';  // Очистка правого блока

    if (query && Object.keys(data).length > 0) {
        // Прохождение по всем департаментам
        for (var globalDepartment in data) {
            var departments = data[globalDepartment];

            // Прохождение по отделам внутри департамента
            for (var department in departments) {
                var departmentHeader = document.createElement('h3');
                departmentHeader.textContent = department;
                departmentHeader.classList.add('department-header');
                staticTablesDiv.appendChild(departmentHeader);

                // Создание таблицы с сотрудниками (раскрыта по умолчанию)
                var table = document.createElement('table');
                table.classList.add('department-table');
                table.style.display = 'table';  // Показ таблицы

                var tbody = document.createElement('tbody');

                departments[department].forEach(function (user) {
                    var row = document.createElement('tr');
                    row.innerHTML = '<td>' + user.ip_phone + '</td>' +
                                    '<td>' + user.name + '</td>' +
                                    '<td>' + user.position + '</td>' +
                                    '<td><a href="mailto:' + user.email + '">' + user.email + '</a></td>' +
                                    '<td>' + user.mobile_phone + '</td>';
                    tbody.appendChild(row);
                });

                table.appendChild(tbody);
                staticTablesDiv.appendChild(table);
            }
        }
    } else {
        staticTablesDiv.innerHTML = '<p class="not-found">Не найдено</p>';
    }
}

// Основная функция обработки ввода в поле поиска
document.getElementById('search').addEventListener('input', function () {
    var query = this.value.trim();
    fetch('/search?query=' + encodeURIComponent(query))
        .then(response => response.json())
        .then(data => {
            if (query) {
                handleSearch(query, data);  // Отображение результатов поиска
                disableGlobalDepartmentClicks();  // Деактивация кликов по департаментам
            } else {
                loadGlobalDepartments();  // Загрузка все департаменты
                enableGlobalDepartmentClicks();  // Активация кликов по департаментам
                document.getElementById('static-tables').innerHTML = '';  // Очистка правого блока
            }
        });
});

// Вызов функции для отображения статичных заголовков при загрузке страницы
window.onload = function () {
    loadGlobalDepartments();  // Загрузка департаментов в левом блоке div2
    document.getElementById('static-tables').innerHTML = '';  // Очистка правого блока div4
};