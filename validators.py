import os
import sqlite3 as sq
from string import ascii_letters, digits

from crud import Friends


CYRILLIC = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЫЭЮЯ'
CHARS = ascii_letters + digits + ' _-'
CHARS_CYR = ascii_letters + CYRILLIC + ' _-'
PATH = os.path.dirname(os.path.abspath(__file__)) + r"\data\database.db"


class FriendsValidators:
    def __init__(self):
        self.obj = Friends()

    @staticmethod
    def validate_name(name):
        if type(name) != str:
            return False
        if len(name) < 2:
            return False
        if not all(map(lambda x: x in CHARS_CYR, name)):
            return False
        return True

    def validate_unique_name(self, name):
        data = self.obj.read()
        if name in {x[1] for x in data}:
            return False
        return True

    @staticmethod
    def validate_id(id):
        if type(id) != int:
            return False
        if id <= 0:
            return False
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM friend")
            data = cur.fetchall()
        if id not in [int(x[0]) for x in data]:
            return False
        return True


class FriendComputerValidator:

    @staticmethod
    def validate_id(friend_id, comp_id):
        if type(friend_id) != int or type(comp_id) != int:
            return False
        if friend_id <= 0 or comp_id <= 0:
            return False
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM friend_computers")
            data = cur.fetchall()
        if friend_id not in {
            int(x[0]) for x in data
            } or comp_id not in {
                int(x[1]) for x in data
                }:
            return False
        return True


class ComputerValidator:

    @staticmethod
    def validate_name_and_status(name):
        if type(name) != str:
            return False
        if len(name) < 2:
            return False
        if not all(map(lambda x: x in CHARS, name)):
            return False
        return True

    @staticmethod
    def validate_id_existance(id):
        if type(id) != int:
            return False
        if id <= 0:
            return False
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM computer")
            data = cur.fetchall()
        if id not in [int(x[0]) for x in data]:
            return False
        return True


class ProcessorValidator:

    @staticmethod
    def validate_correct_name(tpe, frequency):
        if type(tpe) != str or type(frequency) != int:
            return False
        if frequency <= 0:
            return False
        return True

    @staticmethod
    def validate_doubles_existance(tpe, frequency):
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM processor")
            data = cur.fetchall()
        if (tpe.upper(), frequency) in [(x[1], x[2]) for x in data]:
            return False
        return True


class MotherboardValidator:

    @staticmethod
    def validate_correct_name(tpe, socket):
        if tpe == '' or socket == '':
            return False
        if type(tpe) != str or type(socket) != str:
            return False
        if not all(map(lambda x: x in CHARS, tpe)) or \
                not all(map(lambda x: x in CHARS, socket)):
            return False
        return True

    @staticmethod
    def validate_doubles_existance(tpe, socket):
        with sq.connect(PATH) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM motherboard")
            data = cur.fetchall()
        if (tpe.lower(), socket.lower()) in \
                [(x[1].lower(), x[2].lower()) for x in data]:
            return False
        return True
