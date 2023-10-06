# :technologist: My Friends' Computers
**My Friends' Computers** - это desktop-приложение на Python для учета компьютеров друзей, с возможностью добавления, чтения, редактирования, удаления данных о друзьях, их компьютеров и комплектующих, а также формирования и сохранения PDF-отчета.

# Посмотреть, как выглядит интерфейс программы и как работает
Вы можете ознакомиться с внешним видом и работой программы на сайте YouTube по этой [ссылке](https://youtu.be/HwhfAeMtmf8)

## :atom: Технологии
- Python 3.11 со стандартной библиотекой tkinter
- SQLite
- ttkbootstrap 1.10.1
- reportlab 4

## :electron: Техническое описание
Программа спроектирована с использованием объектно-ориентированной парадигмы программирования (ООП). Для хранения данных используется реляционная база данных, управление которой производится с помощью инструментов стандартной библиотеки Python SQLite. Полностью реализована система CRUD. Запросы в базу данных выполняются почти на чистом языке запросов SQL (с диалектом SQLite). Отношения между таблицами в базе данных следующие:
- :family_man_man_girl_girl: Many-to-Many (Многие-ко-Многим)
- :family_man_man_girl: Many-to-One (Один-ко-многим)

## :floppy_disk: Exe-версия приложения для Windows
1. Перейдите по ссылке https://drive.google.com/file/d/1zeWYr9kat39Vb8RHP3DNtzvUXy_dTX8W/view?usp=drive_link
2. Скачайте zip-архив с программой My Friends Computers
3. Распакуйте архив  в любое место
4. Запустите "My Friends Comuters.exe"

## :newspaper: Как пользоваться exe-версией My Friends' Computers
1. Распакуйте архив из папки exe в любом месте. В папке MyFriendsComputers найдите exe-файл MyFriendsComputers.exe
2. Вам откроется стартовое окно программы с предустановленной базой данных.
3. Если вы хотите создать свою базу данных, просто удалите папку data c файлом database.db и вновь запустите программу. Данные обнулятся.
4. После того как вы поработали с данными и хотите получить отчет о компьютерах друга надо выбрать друга в главном окне и нажать кнопку "Скачать PDF".
5. Выберите место для сохранения, и можете изменить название сохраняемого PDF-файла
6. Чтобы прочитать или распечатать PDF-файла его нужно будет открыть любой программой для чтения PDF


## Установка на локальный компьютер в коде Python
_Перед установкой у вас должен уже быть установлен Python версии 3.9+_
### :window: для Windows
1. Скопируйте репозиторий к себе на компьютер по SSH-ключу
```git@github.com:IvanZaycev0717/my_friends_computers.git```

2. Установите виртуальное окружение
```python -m venv venv```

3. Активируйте виртуальное окружение
```source venv/Scripts/activate```

4. Установите внешние библиотеки, выполнив:
```pip install -r requirements.txt```

5. Запустите файл main.py

### :penguin: для Linux/Ubuntu
1. Скопируйте репозиторий к себе на компьютер по SSH-ключу
```git@github.com:IvanZaycev0717/my_friends_computers.git```

2. Установите виртуальное окружение
```python3 -m venv env```

3. Активируйте виртуальное окружение
```source env/bin/activate```

4. Установите внешние библиотеки, выполнив:
```pip install -r requirements.txt```

5. Запустите файл main.py

## :mage: Автор
**Иван Зайцев ivzaycev0717@yandex.ru
(c) 2023**
