# :technologist: My Friends' Computers
**My Friends' Computers** - это desktop-приложение на Python для учета компьютеров друзей, с возможностью добавления, чтения, редактирования, удаления данных о друзьях, их компьютеров и комплектующих, а также формирования и сохранения PDF-отчета.

![my_friends](https://github.com/IvanZaycev0717/my_friends_computers/assets/111955306/42859074-ad4a-4901-931f-e0172e925f87)


## :atom: Технологии
- Python 3.11 со стандартной библиотекой tkinter
- SQLite
- ttkbootstrap 1.10.1
- reportlab 4

## :electron: Техническое описание
Программа спроектирована с использованием объектно-ориентированной парадигмы программирования (ООП). Для хранения данных используется реляционная база данных, управление которой производится с помощью инструментов стандартной библиотеки Python SQLite. Запросы в базу данных выполняются на чистом языке запросов SQL. Отношения между таблицами в базе данных следующие:
- :family_man_man_girl_girl: Many-to-Many (Многие-ко-Многим)
- :family_man_man_girl: Many-to-One (Один-ко-многим)

## Установка на локальный компьютер
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
