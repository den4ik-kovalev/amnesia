# Описание
Amnesia - приложение для хранения паролей и логинов

# Руководство пользователя

## Пин-код
При запуске приложения необходимо ввести пин-код. По умолчанию это "0000". 
Изменить пин-код можно, отредактировав поле pin в файле данных (5-я кнопка на панели).

## Функционал
Кнопки на панели разблокируются после ввода корректного пин-кода. Разберемся, какая кнопка за что отвечает.

### Первая кнопка
Список ваших записей в виде карточек. Первый клик по карточке выделяет её копирует логин в буфер обмена. Второй клик - копирует пароль. Третий - снимает выделение.

### Вторая кнопка
Поиск записи по имени или логину

### Третья кнопка
Добавить новую запись

### Четвертая кнопка
Удалить выделенную запись

### Пятая кнопка
Открыть файл с данными для редактирования

## Файл данных
Настройки приложения и все записи с паролями хранятся в файле формата YAML.
Расположение файла: Папка пользователя -> .amnesia -> data.yml

- Поле "pin" отвечает за пин-код
- Поле "web_mode" за веб-режим
- Поле "records" за записи с паролями

Редактировать имеющиеся записи можно только через файл данных.

## Светодиод
На верхней панели расположен светодиод, который мигает зеленым в случае успеха и красным в случае неудачи.

## Веб-режим
Веб режим включается в файле данных и отвечает за отображение приложения в браузере вместо десктопной версии.

## Логирование
Файл логов автоматически создается рядом с исполняемым файлом.

# Исполняемый файл
EXE находится в директории output



