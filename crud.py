
import sqlite3 as sq
import os


PATH = os.path.dirname(os.path.abspath(__file__)) + r"\data\database.db"


class Friends:
    """Реализует CRUD для таблицы друзей в БД."""

    def create(self, name):
        """Создает нового друга в БД,"""
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute(f"INSERT INTO friend (name) VALUES('{name}');")

    def read(self, *args):
        """Возвращает данные из БД о друзьях."""
        if len(args) == 0:
            with sq.connect(PATH) as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM friend")
                return cur.fetchall()
        elif len(args) == 1:
            with sq.connect(PATH) as con:
                cur = con.cursor()
                cur.execute(f"SELECT * FROM friend WHERE id='{args[0]}'")
                return cur.fetchone()

    def update(self, id, name):
        """Обновляет данные о друге в БД."""
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute(f"""
            UPDATE friend
            SET name='{name}'
            WHERE friend.id='{id}';
            """)

    def delete(self, id):
        """Удаляет данные о друге в БД,"""
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute(f"DELETE FROM friend WHERE id='{id}';")


class Friend_Computer:
    """Является промежуточной таблицой между друзьями и клмпьютерами."""

    def add_computer_to_friend(self, friend_id, comp_id):
        """Добавляет компьютер другу."""
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute(
             f"INSERT INTO friend_computers VALUES ({friend_id}, {comp_id});"
                )

    def get_list_of_friend_compters(self):
        """Возвращает список компьютеров друзей."""
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute("""
            SELECT friend.name, computer.name, computer.status
            FROM friend
            LEFT JOIN friend_computers ON friend_computers.friend_id=friend.id
            LEFT JOIN computer ON friend_computers.comp_id=computer.id
            """)
            print(cur.fetchall())

    def get_particular_friend_computer(self, id):
        """Возвращает список компьютеров для друга."""
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute(f"""
            SELECT computer.id
            FROM friend
            LEFT JOIN friend_computers ON friend_computers.friend_id=friend.id
            LEFT JOIN computer ON friend_computers.comp_id=computer.id
            WHERE friend.id='{id}';
            """)
            return cur.fetchall()

    def edit_friend_computer(self, friend_id, comp_id):
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute(f"""
                UPDATE friend_computers
                SET name='{friend_id}', comp_id='{comp_id}'
                """)

    def delete_friend_computer(self, friend_id, comp_id):
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute(f"""
                DELETE FROM friend_computers
                WHERE friend_id='{friend_id}' AND comp_id='{comp_id}'
                """)


class Computer:

    def create(self, name, status, proc_id, moth_id):
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute(
                f"""INSERT INTO computer
                (name, status, proc_id, moth_id)
                VALUES('{name}', '{status}', '{proc_id}', '{moth_id}');""")

    def read(self, *args):
        if len(args) == 0:
            with sq.connect(PATH) as con:
                cur = con.cursor()
                cur.execute("""
                SELECT computer.id, name, status, processor.type,
                motherboard.type
                FROM computer
                JOIN processor ON computer.proc_id = processor.id
                JOIN motherboard ON computer.moth_id = motherboard.id
                """)
                return cur.fetchall()
        elif len(args) == 1:
            with sq.connect(PATH) as con:
                cur = con.cursor()
                cur.execute(f"""
                SELECT computer.id, name, status,
                processor.type, processor.frequency,
                motherboard.type, motherboard.socket
                FROM computer
                JOIN processor ON computer.proc_id = processor.id
                JOIN motherboard ON computer.moth_id = motherboard.id
                WHERE computer.id='{args[0]}'
                """)
                return cur.fetchone()
        elif len(args) == 2:
            with sq.connect(PATH) as con:
                cur = con.cursor()
                cur.execute(f"""
                SELECT computer.moth_id,
                computer.proc_id
                FROM computer
                JOIN processor ON computer.proc_id = processor.id
                JOIN motherboard ON computer.moth_id = motherboard.id
                WHERE computer.id='{args[0]}'
                """)
                return cur.fetchone()
        else:
            raise ValueError("It takes no arguments or one, got more than 1")

    def update(self, id, name, status, proc_id, moth_id):
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute(f"""
            UPDATE computer
            SET name='{name}',
            status='{status}',
            proc_id='{proc_id}',
            moth_id='{moth_id}'
            WHERE computer.id='{id}';
            """)

    def delete(self, id):
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute(f"DELETE FROM computer WHERE id='{id}';")


class Processor:

    def create(self, tpe, frequency):
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute(
                f"""INSERT INTO processor
                (type, frequency)
                VALUES('{tpe}', '{frequency}');"""
                )

    def read(self, *args):
        if len(args) == 0:
            with sq.connect(PATH) as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM processor")
                return cur.fetchall()
        elif len(args) == 1:
            if type(args[0]) != int:
                raise TypeError("ID must be integer")
            with sq.connect(PATH) as con:
                cur = con.cursor()
                cur.execute(
                    f"""SELECT type, frequency
                    FROM processor
                    WHERE id='{args[0]}'"""
                    )
                return cur.fetchone()
        else:
            raise ValueError("It takes no arguments or one, got more than 1")

    def update(self, id, tpe, frequency):
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute(
                f"""UPDATE processor
                SET type='{tpe.upper()}', frequency='{frequency}'
                WHERE id='{id}';"""
                )

    def delete(self, id):
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute(f"DELETE FROM processor WHERE id='{id}';")


class Motherboard:

    def create(self, tpe, socket):
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute(f"""INSERT INTO motherboard (type, socket)
            VALUES('{tpe}', '{socket}');""")

    def read(self, *args):
        if len(args) == 0:
            with sq.connect(PATH) as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM motherboard")
                return cur.fetchall()
        elif len(args) == 1:
            with sq.connect(PATH) as con:
                cur = con.cursor()
                cur.execute(
                    f"""SELECT type, socket
                    FROM motherboard
                    WHERE id='{args[0]}'"""
                    )
                return cur.fetchone()
        else:
            raise ValueError("It takes no arguments or one, got more than 1")

    def update(self, id, tpe, socket):
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute(
                f"""UPDATE motherboard
                SET type='{tpe}', socket='{socket}'
                WHERE id='{id}';"""
                )

    def delete(self, id):
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute(f"DELETE FROM motherboard WHERE id='{id}';")
