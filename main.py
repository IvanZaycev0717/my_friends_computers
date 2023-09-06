from io import BytesIO
import tkinter as tk
from tkinter.filedialog import asksaveasfilename

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, TableStyle, Table
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import ttkbootstrap as ttk

from create_database import create_db
from crud import Friends, Friend_Computer, Computer, Processor, Motherboard
from settings import FONT, ERROR, SUCCESS, WINDOW_SIZE
from validators import (ComputerValidator, FriendsValidators,
                        MotherboardValidator, ProcessorValidator)


class App(ttk.Window):
    """Создает главное окно программы."""

    def __init__(self, title: str, size: tuple):

        # Инициализатор родительского класса
        super().__init__(themename='journal')

        # Название окна
        self.title(title)

        # Иконка окна
        self.iconbitmap('logo.ico')

        # Размещает окно по центру экрана с любым разрешением
        display_width = self.winfo_screenwidth()
        display_heigth = self.winfo_screenheight()
        left = int(display_width / 2 - size[0] / 2)
        top = int(display_heigth / 2 - size[1] / 2)
        self.geometry(f'{size[0]}x{size[1]}+{left}+{top}')

        # Запрещает изменять размер окна
        self.resizable(False, False)

        # Экземпляры соответсвующих классов
        self.friend_obj = Friends()
        self.comp_obj = Computer()
        self.friend_comp_obj = Friend_Computer()

        # Создание сетки для размещения виджетов
        self.rowconfigure((0, 1, 2, 3,), weight=1)
        self.columnconfigure((0, 1), weight=1)

        self.table_updrater = None

        # Создает виджеты в главном окне
        self.create_widget()

        # Обработка событий
        self.table_friends.bind(
            '<<TreeviewSelect>>', self.select_friend_and_get_computers
            )

        # Вставка данных во все таблицы
        self.insert_friends_data()

        # Делает главное окно доступным из других класов
        global main_window
        main_window = self

        # Закрывает программу при клике на "Х"
        self.mainloop()

    def create_widget(self):
        """Создает виджеты в главном окне."""
        ttk.Label(
            self,
            text='Это мои друзья:',
            font=FONT).grid(
            row=0,
            column=0,
            sticky='ws',
            padx=10
        )
        ttk.Label(
            self,
            text='А это их компьютеры: ',
            font=FONT).grid(
            row=0,
            column=1,
            sticky='ws',
            padx=10
        )

        # Таблица выбора друзей
        self.table_friends = ttk.Treeview(
            self,
            column=('id', 'name'),
            show='headings',
            bootstyle='danger'
        )
        self.table_friends.heading('id', text='ID друга', anchor=tk.W)
        self.table_friends.heading('name', text='Имя', anchor=tk.W)
        self.table_friends.column('id', width=70)
        self.table_friends.column('name', width=190)

        # Создает ползунок прокрутки таблицы друзей
        self.scr_friends = ttk.Scrollbar(
            self,
            orient='vertical',
            command=self.table_friends.yview
        )
        self.table_friends.configure(yscrollcommand=self.scr_friends.set)
        self.scr_friends.place(x=263, y=69, relheight=0.44)

        self.table_friends.grid(
            row=1,
            column=0,
            sticky='nw',
            columnspan=1,
            padx=10
            )

        self.table_computers = ttk.Treeview(
            self,
            column=('name', 'status', 'processor', 'motherboard'),
            show='headings',
            bootstyle='danger')
        self.table_computers.heading(
            'name',
            text='Имя компьютера',
            anchor=tk.W
            )
        self.table_computers.heading(
            'status',
            text='Исправен',
            anchor=tk.W
            )
        self.table_computers.heading(
            'motherboard',
            text='Материнская плата',
            anchor=tk.W
            )
        self.table_computers.heading(
            'processor',
            text='Процессор',
            anchor=tk.W
            )

        self.table_computers.column('#0', minwidth=0, width=0, stretch=False)
        self.table_computers.column(
            'name',
            minwidth=30,
            width=120,
            stretch=False
            )
        self.table_computers.column(
            'status',
            minwidth=30,
            width=80,
            stretch=False
            )
        self.table_computers.column(
            'motherboard',
            minwidth=100,
            width=220,
            stretch=False
            )
        self.table_computers.column(
            'processor',
            minwidth=100,
            width=220,
            stretch=False
            )

        # Создает ползунок прокрутки таблицы компьютеров
        self.scr_computers = ttk.Scrollbar(
            self,
            orient='vertical',
            command=self.table_computers.yview
            )
        self.table_computers.configure(yscrollcommand=self.scr_computers.set)
        self.scr_computers.place(x=928, y=69, relheight=0.44)

        self.table_computers.grid(
            row=1,
            column=1,
            sticky='nw',
            columnspan=1,
            padx=10
            )

        # Создает кнопки
        ttk.Button(
            self,
            text='Добавить друга и комплектующие',
            command=self.open_editor).grid(
            row=2,
            column=0,
            sticky='nsew',
            padx=10,
            pady=10
            )
        self.btn_pdf = ttk.Button(
            self,
            text='Скачать PDF',
            command=self.save_as_pdf,
            state=tk.DISABLED
            )
        self.btn_pdf.grid(
            row=2,
            column=1,
            rowspan=2,
            sticky='nwes',
            padx=10,
            pady=10
            )

        # Подпись автора - меня, Ивана Зайцева
        ttk.Label(
            self,
            text='ivzaycev0717@yandex.ru\n(с) 2023',
            font=FONT).grid(
            row=3,
            column=0,
            sticky='nw',
            padx=10
            )

    def open_editor(self):
        """Открывает окно ражима редактора."""
        global editor_window
        editor_window = FullDataBaseWindow()
        editor_window.focus()

    def insert_friends_data(self):
        """Добавляет данные друзей в таблицу друзей."""
        self.clear_table(self.table_friends)
        self.data = self.friend_obj.read()
        for i in self.data:
            self.table_friends.insert(parent='', index=0, values=i)

    def select_friend_and_get_computers(self, event):
        """Выводит список компьютеров при выборе друга."""
        for i in self.table_friends.selection():
            self.table_updrater = self.table_friends.item(i)['values'][0]
            computers_id = self.friend_comp_obj.get_particular_friend_computer(
                self.table_updrater
                )
            self.current_friend = self.friend_obj.read(self.table_updrater)[1]
            self.clear_table(self.table_computers)
            if computers_id[0][0] is None:
                self.btn_pdf.configure(state=tk.DISABLED)
            else:
                self.btn_pdf.configure(state=tk.NORMAL)
                for i in computers_id:
                    if i[0] is None:
                        continue
                    else:
                        data = self.get_full_info(self.comp_obj.read(i[0]))
                        if data is not None:
                            self.table_computers.insert(parent='',
                                                        index=0,
                                                        values=data
                                                        )

    def update_table(self):
        """Обновляет таблицу с компьютерами друзей."""
        self.clear_table(self.table_computers)
        computers_id = self.friend_comp_obj.get_particular_friend_computer(
            self.table_updrater
            )
        for i in computers_id:
            if i[0] is None:
                continue
            else:
                data = self.get_full_info(self.comp_obj.read(i[0]))
                self.table_computers.insert(parent='', index=0, values=data)

    def clear_table(self, table):
        """Очищает таблицы."""
        for item in table.get_children():
            table.delete(item)

    def get_full_info(self, data):
        """Конвертирует данные из БД в удобный для пользователя вид."""
        try:
            lst = []
            lst.append(data[1])
            lst.append(f'{"Неисправен" if data[2] == 0 else "Исправен"}')
            lst.append(f'{data[3]} {str(data[4])} МГц')
            lst.append(f'{data[5]} {data[6]}')
            return lst
        except TypeError:
            pass

    def save_as_pdf(self, file_path=None):
        """Сохраняет PDF-файл по выбранному пользователем адресу."""
        pdf_file = BytesIO()
        pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf'))
        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        story = []

        data = [
            self.table_computers.item(row_id)['values']
            for row_id in self.table_computers.get_children()
            ]
        add_info = [
            'У вашего друга',
            f'{self.current_friend}',
            'следующие',
            'компьютеры: '
            ]
        data.append(add_info)
        data.reverse()

        tblstyle = TableStyle(
            [('FONT', (0, 0), (-1, len(data)-1), 'DejaVuSerif', 8)]
            )
        tbl = Table(data)
        tbl.setStyle(tblstyle)
        story.append(tbl)
        if file_path is None:
            file_path = asksaveasfilename(
                filetypes=(
                    ("PDF-файл", "*.pdf"),
                    ("All files", "*.*"),
                ),
                initialfile=(f"{self.current_friend}_computers.pdf"),
            )
        doc.title = f'''У вашего друга
          {self.current_friend}
            следующие компьютеры: '''
        doc.build(story)
        pdf_file.seek(0)
        if file_path:
            with open(file_path, 'wb') as f:
                f.write(pdf_file.getbuffer())


class FullDataBaseWindow(ttk.Toplevel):
    """Создает окно режима редактора."""

    def __init__(self):
        super().__init__()
        self.title('My firends computers - Режим редактора')
        self.geometry('950x650')
        self.resizable(False, False)
        self.iconbitmap('logo.ico')

        # Создает сетку для размещения виджетов
        self.rowconfigure((0, 1), weight=1)
        self.columnconfigure((0, 1), weight=1)

        self.moth_frame = FullDataFrames(
            self,
            0,
            self.open_add_mother_window,
            self.open_edit_mother_window,
            'Список материнских плат: ',
            'id',
            'type',
            'socket').grid(row=0, column=0, padx=10)
        self.proc_frame = FullDataFrames(
            self,
            1,
            self.open_add_processor_window,
            self.open_edit_processor_window,
            'Список процессоров: ',
            'id',
            'type',
            'frequency').grid(row=0, column=1, padx=10)
        self.comp_frame = FullDataFrames(
            self,
            2,
            self.open_add_computer_window,
            self.open_edit_computer_window,
            'Список компьютеров: ',
            'id',
            'name',
            'status',
            'proc',
            'moth').grid(row=1, column=0, padx=10)
        self.friend_frame = FullDataFrames(
            self,
            3,
            self.open_add_friend_window,
            self.open_edit_friend_window,
            'Список друзей: ',
            'id',
            'name').grid(row=1, column=1, padx=10)

    def open_add_mother_window(self):
        """Открывет окно добавления материнской платы."""
        global add_mother_window
        add_mother_window = AddMotherWindow()
        add_mother_window.position_center()
        add_mother_window.focus()

    def open_add_processor_window(self):
        """Открывет окно добавления процессора."""
        global add_proc_window
        add_proc_window = AddProcessorWindow()
        add_proc_window.position_center()
        add_proc_window.focus()

    def open_add_computer_window(self):
        """Открывет окно добавления компьютера."""
        global add_comp_window
        add_comp_window = AddCompuerWindow()
        add_comp_window.focus()

    def open_add_friend_window(self):
        """Открывет окно добавления друга."""
        global add_friend_window
        add_friend_window = AddFriendWindow()
        add_friend_window.position_center()
        add_friend_window.focus()

    def open_edit_mother_window(self):
        """Открывет окно реадктирования материнской платы."""
        global edit_mother_window
        edit_mother_window = EditMotherWindow()
        edit_mother_window.position_center()
        edit_mother_window.focus()

    def open_edit_processor_window(self):
        """Открывет окно реадктирования процессора."""
        global edit_proc_window
        edit_proc_window = EditProcessorWindow()
        edit_proc_window.position_center()
        edit_proc_window.focus()

    def open_edit_computer_window(self):
        """Открывет окно реадктирования компьютера."""
        global edit_computer_window
        edit_computer_window = EditComputersWindow()
        edit_computer_window.position_center()
        edit_computer_window.focus()

    def open_edit_friend_window(self):
        """Открывет окно реадктирования друга."""
        global edit_friend_window
        edit_friend_window = EditFriendWindow()
        edit_friend_window.position_center()
        edit_friend_window.focus()


class FullDataFrames(ttk.Frame):
    """Создает рамки с виджетами для окна режима редактора."""

    def __init__(self, parent, number, btn_cmd, btn_edit, label_txt, *args):
        super().__init__(parent)
        self.number = number
        self.label_txt = label_txt
        self.btn_cmd = btn_cmd
        self.btn_edit = btn_edit
        self.args = args
        self.create_widgets()

    def create_widgets(self):
        """Создает виджеты в рамке."""
        ttk.Label(self, text=self.label_txt).pack(fill='x')
        self.current_table = ttk.Treeview(
            self,
            columns=self.args,
            show='headings',
            bootstyle='danger'
            )
        length = len(self.args)
        for number, field in enumerate(self.args):
            width = int(450/length)
            self.current_table.heading(field, text=field, anchor=tk.W)
            self.current_table.column(field, width=width, anchor='w')

        self.current_table.pack(fill='x')
        scrollbar = ttk.Scrollbar(
            self,
            orient='vertical',
            command=self.current_table.yview
            )
        self.current_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.place(x=444, y=50, relheight=0.63)
        self.insert_data()

        ttk.Button(
            self,
            text='Добавить',
            command=self.btn_cmd).pack(side='left', pady=5)
        ttk.Button(
            self,
            text='Редактировать',
            command=self.btn_edit).pack(side='right', pady=5)

    def insert_data(self):
        """Вставляет данные в виджеты."""
        data_db = (
            Motherboard().read(),
            Processor().read(),
            Computer().read(),
            Friends().read()
            )
        self.data = data_db[self.number]
        for i in self.data:
            self.current_table.insert(parent='', index=0, values=i)

    def delete_data(self):
        """Удаляет данные из виджетов."""
        self.current_table.delete(*self.current_table.get_children())


class AddMotherWindow(ttk.Toplevel):
    """Создает окно добавления материнской платы."""

    def __init__(self):
        super().__init__()
        self.title('My firends computers - Добавить материнскую плату')
        self.geometry('600x200')
        self.resizable(False, False)
        self.iconbitmap('logo.ico')

        # Экземпляры соответсвующих классов
        self.moth_obj = Motherboard()
        self.validator = MotherboardValidator()

        # Переменные GUI
        self.mb_type = ttk.StringVar()
        self.mb_socket = ttk.StringVar()
        self.error_socket = ttk.StringVar()
        self.success_socket = ttk.StringVar()

        # Создание виджетов
        self.label_type = ttk.Label(
            self,
            text='Марка материнской платы: ').pack(anchor='w', padx=10)
        self.entry_type = ttk.Entry(
            self,
            textvariable=self.mb_type).pack(fill='x', padx=10)
        self.label_socket = ttk.Label(
            self,
            text='Сокет материнской платы: ').pack(anchor='w', padx=10)
        self.entry_socket = ttk.Entry(
            self,
            textvariable=self.mb_socket).pack(fill='x', padx=10)
        self.error_label_socket = ttk.Label(
            self,
            textvariable=self.error_socket,
            foreground=ERROR).pack(anchor='w', padx=10)
        self.success_label_socket = ttk.Label(
            self,
            textvariable=self.success_socket,
            foreground=SUCCESS).pack(anchor='center', padx=10)
        self.btn_add = ttk.Button(
            self,
            text='Добавить',
            command=self.add).pack(side='left', padx=20)
        self.btn_cancel = ttk.Button(
            self,
            text='Отмена',
            command=self.cancel).pack(side='right', padx=20)

    def cancel(self):
        """Закрывает окно добавления материнской платы."""
        add_mother_window.destroy()

    def add(self):
        """Добавляет новую запись материнской платы в БД."""
        m_type = self.mb_type.get().replace(' ', '_')
        m_socket = self.mb_socket.get()
        if not self.validator.validate_correct_name(m_type, m_socket):
            self.success_socket.set('')
            self.error_socket.set(
                'Некорректное название типа материнской платы'
                )
        elif not self.validator.validate_doubles_existance(m_type, m_socket):
            self.success_socket.set('')
            self.error_socket.set('*Такая материнская плата уже существует')
        else:
            self.error_socket.set('')
            self.success_socket.set('Материнская плата успешно добавлена')
            self.moth_obj.create(m_type, m_socket)
            self.update_editor()

    def update_editor(self):
        """Обновляет таблицу материнских плат в окне режима редактора."""
        editor_window.__dict__['children']['!fulldataframes'].delete_data()
        editor_window.__dict__['children']['!fulldataframes'].insert_data()


class AddProcessorWindow(ttk.Toplevel):
    """Создает окно добавления процессора."""

    def __init__(self):
        super().__init__()
        self.title('My firends computers - Добавить процессор')
        self.geometry('600x200')
        self.resizable(False, False)
        self.iconbitmap('logo.ico')

        # Экземпляры соответсвующих классов
        self.proc_obj = Processor()
        self.validator = ProcessorValidator()

        # Переменные GUI
        self.pr_type = ttk.StringVar()
        self.pr_frequency = ttk.IntVar()
        self.error_socket = ttk.StringVar()
        self.success_socket = ttk.StringVar()

        # Создание виджетов
        self.label_type = ttk.Label(
            self,
            text='Марка процессора: ').pack(anchor='w', padx=10)
        self.entry_type = ttk.Entry(
            self,
            textvariable=self.pr_type).pack(fill='x', padx=10)
        self.label_frequency = ttk.Label(
            self,
            text='Частота процессора (МГц): ').pack(anchor='w', padx=10)
        self.entry_socket = ttk.Entry(
            self,
            textvariable=self.pr_frequency).pack(fill='x', padx=10)
        self.error_label_frequency = ttk.Label(
            self,
            textvariable=self.error_socket,
            foreground=ERROR).pack(anchor='w', padx=10)
        self.success_label_socket = ttk.Label(
            self,
            textvariable=self.success_socket,
            foreground=SUCCESS).pack(anchor='center', padx=10)
        self.btn_add = ttk.Button(
            self,
            text='Добавить',
            command=self.add).pack(side='left', padx=20)
        self.btn_cancel = ttk.Button(
            self,
            text='Отмена',
            command=self.cancel).pack(side='right', padx=20)

    def cancel(self):
        """Закрывает окно добавления процессора."""
        add_proc_window.destroy()

    def add(self):
        """Добавляет в БД новую запись о процессоре."""
        try:
            p_type = self.pr_type.get().replace(' ', '_')
            p_freq = self.pr_frequency.get()
            if not self.validator.validate_correct_name(p_type, p_freq):
                self.success_socket.set('')
                self.error_socket.set(
                    '*Некорректно указана марка процессора или частота'
                    )
            elif not self.validator.validate_doubles_existance(p_type, p_freq):
                self.success_socket.set('')
                self.error_socket.set(
                    '*Такой процессор уже есть в базе данных'
                    )
            else:
                self.error_socket.set('')
                self.success_socket.set('Процессор успешно добавлен')
                self.proc_obj.create(p_type, p_freq)
                self.update_editor_table()
        except tk.TclError:
            pass

    def update_editor_table(self):
        """Обновляет таблицу процессоров в окне режима редактировани."""
        editor_window.__dict__['children']['!fulldataframes2'].delete_data()
        editor_window.__dict__['children']['!fulldataframes2'].insert_data()


class AddCompuerWindow(ttk.Toplevel):
    """Создает окно добавления компьютера."""

    def __init__(self):
        super().__init__()
        self.title('My firends computers - Добавить компьютеры')
        self.geometry('450x350')
        self.resizable(False, False)
        self.iconbitmap('logo.ico')

        # Экземпляры соотвующих классов
        self.comp_obj = Computer()
        self.moth_obj = Motherboard()
        self.proc_obj = Processor()
        self.validator = ComputerValidator()

        # Создание сетки для размещения виджетов
        self.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1)
        self.columnconfigure((0, 1), weight=1)

        # Данные для таблиц
        moth_items = [f'{i[0]}. {i[1]} {i[2]}' for i in self.moth_obj.read()]
        proc_items = [f'{i[0]}. {i[1]} {i[2]}' for i in self.proc_obj.read()]

        # Переменные GUI
        self.pc_type = ttk.StringVar()
        self.radio_var = ttk.IntVar()
        self.moth_var = ttk.StringVar(value='Выберите материнскую плату')
        self.proc_var = ttk.StringVar(value='Выберите процессор')
        self.error = ttk.StringVar()
        self.success = ttk.StringVar()
        self.moth_id = None
        self.proc_id = None

        # Виджеты
        ttk.Label(
            self,
            text='Название компьютера: ').grid(
            row=0,
            column=0,
            columnspan=2,
            sticky='new',
            padx=10,
            pady=5
            )
        ttk.Entry(
            self,
            textvariable=self.pc_type).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky='new',
            padx=10
            )
        ttk.Label(
            self,
            text='Статус компьютера: ').grid(
            row=2,
            column=0,
            columnspan=2,
            sticky='new',
            padx=10
            )

        ttk.Radiobutton(
            self,
            text='Исправен',
            value=1,
            variable=self.radio_var).grid(row=3, column=0, sticky='w', padx=10)
        ttk.Radiobutton(
            self,
            text='Неисправен',
            value=0,
            variable=self.radio_var).grid(row=3, column=1, sticky='w', padx=10)

        ttk.Label(
            self,
            text='Материнская плата: ').grid(
            row=4,
            column=0,
            sticky='w',
            padx=10,
            pady=5
            )
        ttk.Label(
            self,
            text='Процессор: ').grid(
            row=4,
            column=1,
            sticky='w',
            padx=10,
            pady=5
            )

        self.moth_combo = ttk.Combobox(
            self,
            textvariable=self.moth_var, state="readonly")
        self.moth_combo.configure(values=moth_items)
        self.moth_combo.grid(
            row=5,
            column=0,
            sticky='we',
            padx=10
            )

        self.proc_combo = ttk.Combobox(
            self,
            textvariable=self.proc_var, state="readonly")
        self.proc_combo.configure(values=proc_items)
        self.proc_combo.grid(row=5, column=1, sticky='we', padx=10)

        ttk.Label(
            self,
            textvariable=self.error,
            foreground=ERROR).grid(row=6, column=0, columnspan=2)
        ttk.Label(
            self,
            textvariable=self.success,
            foreground=SUCCESS).grid(row=7, column=0, columnspan=2)

        ttk.Button(
            self,
            text='Добавить',
            command=self.add_computer).grid(
            row=8,
            column=0,
            sticky='w',
            padx=10)
        ttk.Button(
            self,
            text='Отмена',
            command=self.cancel).grid(
            row=8,
            column=1,
            sticky='e',
            padx=10
            )

        # События в выпадаюх списках
        self.moth_combo.bind('<<ComboboxSelected>>', self.get_moth_id)
        self.proc_combo.bind('<<ComboboxSelected>>', self.get_proc_id)

    def get_moth_id(self, event):
        """Возвращает ID выбранной материской платы."""
        text = self.moth_var.get()
        int_str = ''
        for symbol in text:
            if symbol != '.':
                int_str += symbol
            else:
                break
        self.moth_id = int(int_str)
        return self.moth_id

    def get_proc_id(self, event):
        """Возвращает ID выбранного процессора."""
        text = self.proc_var.get()
        int_str = ''
        for symbol in text:
            if symbol != '.':
                int_str += symbol
            else:
                break
        self.proc_id = int(int_str)
        return self.proc_id

    def cancel(self):
        """Закрывает окно добавления компьютера."""
        add_comp_window.destroy()

    def add_computer(self):
        """Добавляет в БД новую запись о компьютере."""
        try:
            name = self.pc_type.get()
            status = self.radio_var.get()
            moth_id = self.moth_id
            proc_id = self.proc_id
            if not self.validator.validate_name_and_status(name):
                self.error.set('*Ошибка в названии компьютера')
                self.success.set('')
            elif type(moth_id) != int or type(proc_id) != int:
                self.error.set('*Не выбрана материнская плата или процессор')
                self.success.set('')
            else:
                self.error.set('')
                self.success.set('Компьютер успешно добавлен')
                self.comp_obj.create(name, status, proc_id, moth_id)
                self.update_editor()
        except Exception:
            self.error.set('*Ошибка в введенных данных')
            self.success.set('')

    def update_editor(self):
        """Обновляет таблицу компьютеров в окне режима редактора."""
        editor_window.__dict__['children']['!fulldataframes3'].delete_data()
        editor_window.__dict__['children']['!fulldataframes3'].insert_data()


class AddFriendWindow(ttk.Toplevel):
    """Создает окно добавления друга."""

    def __init__(self):
        super().__init__()
        self.title('My firends computers - Добавить друга')
        self.geometry('450x150')
        self.resizable(False, False)
        self.iconbitmap('logo.ico')

        # Grid Creation
        self.rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        self.columnconfigure((0, 1), weight=1)

        # objects
        self.validator = FriendsValidators()
        self.friend_obj = Friends()

        # vars
        self.name_var = ttk.StringVar()
        self.error = ttk.StringVar()
        self.success = ttk.StringVar()

        ttk.Label(
            self,
            text='Имя друга: ').grid(
            row=0,
            column=0,
            columnspan=2,
            sticky='new',
            padx=10,
            pady=5
            )
        ttk.Entry(
            self,
            textvariable=self.name_var).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky='new',
            padx=10
            )

        ttk.Label(
            self,
            textvariable=self.error,
            foreground=ERROR).grid(
            row=4,
            column=0,
            columnspan=2
            )
        ttk.Label(
            self,
            textvariable=self.success,
            foreground=SUCCESS).grid(
            row=5,
            column=0,
            columnspan=2
            )

        ttk.Button(
            self,
            text='Добавить',
            command=self.add_friend).grid(
            row=6,
            column=0,
            sticky='w',
            padx=10,
            pady=5
            )
        ttk.Button(
            self,
            text='Отмена',
            command=self.cancel).grid(
            row=6,
            column=1,
            sticky='e',
            padx=10,
            pady=5
            )

    def cancel(self):
        """Закрывает окно добавления друга."""
        add_friend_window.destroy()

    def add_friend(self):
        """Добавляет в БД новую запись о друге."""
        name = self.name_var.get().replace(' ', '_')
        if not self.validator.validate_name(name):
            self.success.set('')
            self.error.set('*Имя друга содержит недопустимые символы')
        elif not self.validator.validate_unique_name(name):
            self.success.set('')
            self.error.set('*Друг с таким именем уже есть в базе данных')
        else:
            self.success.set('Добавлен друг и его компьютер')
            self.error.set('')
            self.friend_obj.create(name)
            self.update_editor()
            main_window.insert_friends_data()

    def update_editor(self):
        """Обновляет таблицу друзей в окне режима редактора."""
        editor_window.__dict__['children']['!fulldataframes4'].delete_data()
        editor_window.__dict__['children']['!fulldataframes4'].insert_data()


class EditMotherWindow(ttk.Toplevel):
    """Создает окно редактора материнских плат."""

    def __init__(self):
        super().__init__()
        self.title('My firends computers - Редактировать материнскую плату')
        self.geometry('600x300')
        self.resizable(False, False)
        self.iconbitmap('logo.ico')

        # Сетка для размещения виджетов
        self.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1)
        self.columnconfigure((0, 1), weight=1)

        # Экземпляры соответсвующих классов
        self.moth_obj = Motherboard()
        self.validator = MotherboardValidator()

        # Получение данных для выпадающего списка
        self.moth_items = self.get_items()

        # Переменные GUI
        self.moth_var = ttk.StringVar(value='Выберите материнскую плату')
        self.id = ttk.IntVar()
        self.type = ttk.StringVar()
        self.socket = ttk.StringVar()
        self.error = ttk.StringVar()
        self.success = ttk.StringVar()

        # Виджеты
        ttk.Label(
            self,
            text='Редактировать материнскую плату').grid(
            row=0,
            column=0,
            columnspan=2,
            sticky='new',
            padx=10,
            pady=5
            )
        self.moth_combo = ttk.Combobox(
            self,
            textvariable=self.moth_var,
            state='readonly'
            )
        self.moth_combo.configure(values=self.moth_items)
        self.moth_combo.grid(row=1, column=0, sticky='new', padx=10)
        ttk.Button(
            self,
            text='Удалить',
            command=self.delete).grid(
            row=1,
            column=1,
            sticky='nw',
            padx=10
            )
        ttk.Label(
            self,
            text='Изменить марку платы: ').grid(
            row=2,
            column=0,
            columnspan=2,
            sticky='new',
            padx=10,
            pady=5
            )
        ttk.Entry(
            self,
            textvariable=self.type).grid(
            row=3,
            column=0,
            columnspan=2,
            sticky='new',
            padx=10
            )
        ttk.Label(
            self,
            text='Изменить сокет: ').grid(
            row=4,
            column=0,
            columnspan=2,
            sticky='new',
            padx=10,
            pady=5
            )
        ttk.Entry(
            self,
            textvariable=self.socket).grid(
            row=5,
            column=0,
            columnspan=2,
            sticky='new',
            padx=10
            )
        ttk.Label(
            self,
            text='',
            textvariable=self.error,
            foreground=ERROR).grid(
            row=6,
            column=0,
            columnspan=2,
            padx=10
            )
        ttk.Label(
            self,
            text='',
            textvariable=self.success,
            foreground=SUCCESS).grid(
            row=7,
            column=0,
            columnspan=2,
            padx=10
            )
        ttk.Button(
            self,
            text='Сохранить',
            command=self.save).grid(
            row=8,
            column=0,
            padx=10,
            pady=10,
            sticky='nw'
            )
        ttk.Button(
            self,
            text='Отмена',
            command=self.cancel).grid(
            row=8,
            column=1,
            padx=10,
            pady=10,
            sticky='ne'
            )

        # События в выпадающих списках
        self.moth_combo.bind('<<ComboboxSelected>>', self.edit)

    def get_items(self):
        """Получает данные для таблицы материнских плат."""
        return [i for i in self.moth_obj.read()]

    def edit(self, event):
        """Возвращает ID, марку, сокет материнской платы."""
        data = self.moth_var.get().split()
        id, tpe, socket = int(data[0]), data[1], data[2]
        self.id.set(id)
        self.type.set(tpe)
        self.socket.set(socket)

    def update_combo(self):
        """Обновляет информацию в выпадающем списке."""
        self.moth_combo['values'] = self.get_items()

    def save(self):
        """Обновляет информацию в БД о материской плате."""
        id = self.id.get()
        tpe = self.type.get()
        socket = self.socket.get()
        if not self.validator.validate_correct_name(tpe, socket):
            self.error.set('Введена недопустимая марка или сокет')
            self.success.set('')
        else:
            self.error.set('')
            self.success.set('Информация о материнской плате обновлена')
            self.moth_obj.update(id, tpe, socket)
            self.moth_var.set((id, tpe, socket))
            self.update_combo()
            self.update_editor()

    def update_editor(self):
        """Обновляет таблицу материнских плат в окне режима редактирвоания."""
        editor_window.__dict__['children']['!fulldataframes'].delete_data()
        editor_window.__dict__['children']['!fulldataframes'].insert_data()

    def delete(self):
        """Удаляет запись о материнской плате в БД."""
        if not self.id.get():
            self.error.set(
                'Выберите материнскую плату, которую хотите удалить'
                )
            self.success.set('')
        else:
            self.error.set('')
            self.success.set(
                f'Материнская плата {self.id.get()} {self.type.get()} {self.socket.get()} успешно удалена'
                )
            self.moth_obj.delete(self.id.get())
            editor_window.__dict__['children']['!fulldataframes'].delete_data()
            editor_window.__dict__['children']['!fulldataframes'].insert_data()
            self.type.set('')
            self.socket.set('')
            self.moth_var.set('Выберите материнскую плату')
            self.update_combo()

    def cancel(self):
        edit_mother_window.destroy()


class EditProcessorWindow(ttk.Toplevel):
    """Создает окно редактирования процессоров."""

    def __init__(self):
        super().__init__()
        self.title('My firends computers - Редактировать процессор')
        self.geometry('600x300')
        self.resizable(False, False)
        self.iconbitmap('logo.ico')

        self.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1)
        self.columnconfigure((0, 1), weight=1)

        # Экземпляры соответсвяющих классов
        self.proc_obj = Processor()
        self.validator = ProcessorValidator()

        # Переменные GUI
        self.proc_var = ttk.StringVar(value='Выберите процессор')
        self.proc_items = self.get_items()
        self.id = ttk.IntVar()
        self.type = ttk.StringVar()
        self.frequency = ttk.IntVar()
        self.error = ttk.StringVar()
        self.success = ttk.StringVar()

        # Виджеты
        ttk.Label(
            self,
            text='Редактировать процессор').grid(
            row=0,
            column=0,
            columnspan=2,
            sticky='new',
            padx=10,
            pady=5
            )
        self.proc_combo = ttk.Combobox(
            self,
            textvariable=self.proc_var,
            state='readonly'
            )
        self.proc_combo.configure(values=self.proc_items)
        self.proc_combo.grid(row=1, column=0, sticky='new', padx=10)
        ttk.Button(
            self,
            text='Удалить',
            command=self.delete).grid(
            row=1,
            column=1,
            sticky='nw',
            padx=10
            )
        ttk.Label(
            self,
            text='Изменить производителя: ').grid(
            row=2,
            column=0,
            columnspan=2,
            sticky='new',
            padx=10,
            pady=5)
        ttk.Entry(
            self,
            textvariable=self.type).grid(
            row=3,
            column=0,
            columnspan=2,
            sticky='new',
            padx=10
            )
        ttk.Label(
            self,
            text='Изменить значение частоты: ').grid(
            row=4,
            column=0,
            columnspan=2,
            sticky='new',
            padx=10,
            pady=5
            )
        ttk.Entry(
            self,
            textvariable=self.frequency).grid(
            row=5,
            column=0,
            columnspan=2,
            sticky='new',
            padx=10
            )
        ttk.Label(
            self,
            text='',
            textvariable=self.error,
            foreground=ERROR).grid(
            row=6,
            column=0,
            columnspan=2,
            padx=10
            )
        ttk.Label(
            self,
            text='',
            textvariable=self.success, foreground=SUCCESS).grid(
            row=7,
            column=0,
            columnspan=2,
            padx=10
            )
        ttk.Button(
            self,
            text='Сохранить',
            command=self.save).grid(
            row=8,
            column=0,
            padx=10,
            pady=10,
            sticky='nw'
            )
        ttk.Button(
            self,
            text='Отмена',
            command=self.cancel).grid(
            row=8,
            column=1,
            padx=10,
            pady=10,
            sticky='ne'
            )

        # События в выпадающем списке
        self.proc_combo.bind('<<ComboboxSelected>>', self.edit)

    def edit(self, event):
        """Устанавливает значение ID, типа и частоты при выборе."""
        data = self.proc_var.get().split()
        id, tpe, frequency = int(data[0]), data[1], int(data[2])
        self.id.set(id)
        self.type.set(tpe)
        self.frequency.set(frequency)

    def update_combo(self):
        """Обновляет выпадающий список процессоров."""
        self.proc_combo['values'] = self.get_items()

    def get_items(self):
        """Возвращает данные о процессоре из БД."""
        return [i for i in self.proc_obj.read()]

    def cancel(self):
        """Закрывает окно редактирования процессоров."""
        edit_proc_window.destroy()

    def save(self):
        """Обновляет запись о процессоре в БД."""
        try:
            id = self.id.get()
            tpe = self.type.get()
            frequency = self.frequency.get()
            if not self.validator.validate_correct_name(tpe, frequency):
                self.error.set('Введена недопустимая марка или частота')
                self.success.set('')
            elif not self.validator.validate_doubles_existance(tpe, frequency):
                self.error.set(
                    'Процессор с такими характеристиками уже существует'
                    )
                self.success.set('')
            else:
                self.error.set('')
                self.success.set('Информация о процессоре обновлена')
                self.proc_obj.update(id, tpe, frequency)
                self.proc_var.set((id, tpe, frequency))
                self.update_combo()
                self.update_editor()
        except tk.TclError:
            self.error.set('Ошибка в введенных данных')
            self.success.set('')

    def update_editor(self):
        """Обновляет таблицу процессоров в окне режима редактора."""
        editor_window.__dict__['children']['!fulldataframes2'].delete_data()
        editor_window.__dict__['children']['!fulldataframes2'].insert_data()

    def delete(self):
        if not self.id.get():
            self.error.set('Выберите процессор, который хотите удалить')
            self.success.set('')
        else:
            self.error.set('')
            self.success.set(
                f'Процессор {self.id.get()} {self.type.get()} {self.frequency.get()} успешно удален'
                )
            self.proc_obj.delete(self.id.get())
            self.update_editor()
            self.type.set('')
            self.frequency.set('')
            self.proc_var.set('Выберите процессор')
            self.update_combo()


class EditComputersWindow(ttk.Toplevel):
    """Создает окно редактирования компьютеров."""

    def __init__(self):
        super().__init__()
        self.title('My firends computers - Редактировать компьютеры')
        self.geometry('450x350')
        self.resizable(False, False)
        self.iconbitmap('logo.ico')

        # Экземпляры соответсвующих классов
        self.comp_obj = Computer()
        self.moth_obj = Motherboard()
        self.proc_obj = Processor()
        self.validator = ComputerValidator()

        # Сетка для виджетов
        self.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1)
        self.columnconfigure((0, 1), weight=1)

        # Переменные GUI
        self.comp_id = None
        self.moth_id = None
        self.proc_id = None
        self.name = None
        self.comp_var = ttk.StringVar(value='Выберите процессор')
        self.moth_var = ttk.StringVar(value='Выберите материнскую плату')
        self.proc_var = ttk.StringVar(value='Выберите процессор')
        self.error = ttk.StringVar()
        self.success = ttk.StringVar()
        self.comp_items = self.get_items()[0]
        self.moth_items = self.get_items()[1]
        self.proc_items = self.get_items()[2]
        self.radio_var = ttk.IntVar()

        # Виджеты
        ttk.Label(
            self,
            text='Редактировать компьютер: ').grid(
            row=0,
            column=0,
            columnspan=2,
            sticky='new',
            padx=10,
            pady=5
            )

        self.comp_combo = ttk.Combobox(
            self,
            textvariable=self.comp_var,
            state='readonly'
            )
        self.comp_combo.configure(
            values=self.comp_items
            )
        self.comp_combo.grid(row=1, column=0, sticky='new', padx=10)
        ttk.Button(
            self,
            text='Удалить',
            command=self.delete).grid(
            row=1,
            column=1,
            sticky='nw',
            padx=10
            )

        ttk.Label(
            self,
            text='Поменять статус компьютера: ').grid(
            row=2,
            column=0,
            columnspan=2,
            sticky='new',
            padx=10
            )

        ttk.Radiobutton(
            self,
            text='Исправен',
            value=1,
            variable=self.radio_var).grid(
            row=3,
            column=0,
            sticky='w',
            padx=10
            )
        ttk.Radiobutton(
            self,
            text='Неисправен',
            value=0,
            variable=self.radio_var).grid(
            row=3,
            column=1,
            sticky='w',
            padx=10
            )

        ttk.Label(
            self,
            text='Изменить материнскую плату: ').grid(
            row=4,
            column=0,
            sticky='w',
            padx=10,
            pady=5
            )
        ttk.Label(
            self,
            text='Изменить процессор: ').grid(
            row=4,
            column=1,
            sticky='w',
            padx=10,
            pady=5
            )

        self.moth_combo = ttk.Combobox(
            self,
            textvariable=self.moth_var, state="readonly")
        self.moth_combo.configure(values=self.moth_items)
        self.moth_combo.grid(row=5, column=0, sticky='we', padx=10)

        self.proc_combo = ttk.Combobox(
            self,
            textvariable=self.proc_var, state="readonly"
            )
        self.proc_combo.configure(values=self.proc_items)
        self.proc_combo.grid(
            row=5,
            column=1,
            sticky='we',
            padx=10
            )

        ttk.Label(
            self,
            textvariable=self.error,
            foreground=ERROR).grid(
            row=6,
            column=0,
            columnspan=2
            )
        ttk.Label(
            self,
            textvariable=self.success,
            foreground=SUCCESS).grid(row=7, column=0, columnspan=2)

        ttk.Button(
            self,
            text='Сохранить',
            command=self.save).grid(
            row=8,
            column=0,
            sticky='w',
            padx=10
            )
        ttk.Button(
            self,
            text='Отмена',
            command=self.cancel).grid(
            row=8,
            column=1,
            sticky='e',
            padx=10
            )

        # Events
        self.comp_combo.bind('<<ComboboxSelected>>', self.edit)
        self.moth_combo.bind('<<ComboboxSelected>>', self.edit_moth)
        self.proc_combo.bind('<<ComboboxSelected>>', self.edit_proc)

    def get_items(self):
        """Возвразает кортеж их данных из БД."""
        return (
            [i for i in self.comp_obj.read()],
            [i for i in self.moth_obj.read()],
            [i for i in self.proc_obj.read()]
            )

    def cancel(self):
        """Закрывает окно редактирования компьютеров."""
        edit_computer_window.destroy()

    def delete(self):
        """Удаляет запись в БД о данном компьютере."""
        if not self.comp_id:
            self.error.set('Выберите компьютер, который хотите удалить')
            self.success.set('')
        else:
            self.error.set('')
            self.success.set(f'Компьютер {self.comp_var.get()} успешно удален')
            self.comp_obj.delete(self.comp_id)
            self.update_editor()
            self.comp_id = None
            self.update_combo()
            self.comp_var.set('Выберите процессор')
            self.moth_var.set('Выберите материнскую плату')
            self.proc_var.set('Выберите процессор')

    def update_editor(self):
        """Обновляет таблицу компьютеров в окне режима редактора."""
        editor_window.__dict__['children']['!fulldataframes3'].delete_data()
        editor_window.__dict__['children']['!fulldataframes3'].insert_data()

    def update_combo(self):
        """Обновляает данные в выпадающих списках."""
        self.comp_combo['values'] = self.get_items()[0]
        self.moth_combo['values'] = self.get_items()[1]
        self.proc_combo['values'] = self.get_items()[2]

    def edit(self, event):
        """Устанавливает значения характеристи ПК для БД."""
        data = self.comp_var.get().split()
        self.comp_id = int(data[0])
        self.radio_var.set(int(data[2]))
        self.name = data[1]
        self.get_moth_proc_id(self.comp_id)
        self.moth_var.set(self.moth_obj.read(self.moth_id))
        self.proc_var.set(self.proc_obj.read(self.proc_id))

    def edit_moth(self, event):
        """Устанавливает ID выбранной материнской платы."""
        data = self.moth_var.get().split()
        self.moth_id = int(data[0])

    def edit_proc(self, event):
        """Устанавливает ID выбранного процессора."""
        data = self.proc_var.get().split()
        self.proc_id = int(data[0])

    def get_moth_proc_id(self, comp_id):
        """Получает из БД записи о выбранных комплектующих."""
        try:
            ides = self.comp_obj.read(comp_id, 1)
            self.moth_id = ides[0]
            self.proc_id = ides[1]
        except TypeError:
            pass

    def save(self):
        """Обновляет запись в БД выбранного компьютера."""
        if not self.validator.validate_name_and_status(self.name):
            self.error.set('Введенено неверное имя компьютера')
            self.success.set('')
        elif self.comp_id is None:
            self.error.set('*Выберите компьютер')
            self.success.set('')
        else:
            self.error.set('')
            self.success.set('Информация о компьютере успешно обновлена')
            self.comp_obj.update(
                self.comp_id,
                self.name,
                self.radio_var.get(),
                self.proc_id,
                self.moth_id
                )
            self.update_combo()
            self.get_moth_proc_id(self.comp_id)
            self.comp_var.set(self.comp_obj.read(self.comp_id))
            self.moth_var.set(self.moth_obj.read(self.moth_id))
            self.proc_var.set(self.proc_obj.read(self.proc_id))
            self.update_editor()


class EditFriendWindow(ttk.Toplevel):
    """Создает окно редактирования друзей."""

    def __init__(self):
        super().__init__()
        self.title('My firends computers - Редактировать компьютеры друга')
        self.geometry('950x300')
        self.resizable(False, False)
        self.iconbitmap('logo.ico')

        # Создание сетки для размещения виджетов
        self.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        self.columnconfigure((0, 1, 2), weight=1)

        # Экземпляры соответсвующих классов
        self.friend_obj = Friends()
        self.comp_obj = Computer()
        self.friend_comp_obj = Friend_Computer()
        self.validator = FriendsValidators()

        # Переменные
        self.friend_id = None
        self.friend_item = self.get_item()[0]
        self.friend_var = ttk.StringVar(value='Выберите друга')

        self.comp_id = None
        self.comp_item = self.get_item()[1]
        self.comp_var = ttk.StringVar(value='Выберите компьютер')
        self.error = ttk.StringVar()
        self.success = ttk.StringVar()

        # Виджеты
        ttk.Label(
            self,
            text='Выберите друга:').grid(
            row=0,
            column=0,
            padx=10,
            sticky='w',
            pady=5
            )
        ttk.Label(
            self,
            text='Выберите его компьютер в таблице:').grid(
            row=0,
            column=2,
            sticky='w',
            pady=5
            )

        self.friend_combo = ttk.Combobox(
            self,
            textvariable=self.friend_var,
            state='readonly'
            )
        self.friend_combo.configure(values=self.friend_item)
        self.friend_combo.grid(row=1, column=0, sticky='new', padx=10)
        ttk.Button(
            self,
            text='Удалить',
            command=self.delete_friend).grid(
            row=1,
            column=1,
            sticky='nw'
            )
        self.friend_table = ttk.Treeview(
            self,
            column=(
                'id',
                'name',
                'status',
                'processor',
                'motherboard'
            ),
            show='headings', bootstyle='danger')
        self.friend_table.heading('id', text='ID компьютера', anchor=tk.W)
        self.friend_table.heading('name', text='Имя компьютера', anchor=tk.W)
        self.friend_table.heading('status', text='Исправен', anchor=tk.W)
        self.friend_table.heading(
            'motherboard', text='Материнская плата', anchor=tk.W
            )
        self.friend_table.heading('processor', text='Процессор', anchor=tk.W)

        self.friend_table.column('id', minwidth=0, width=0, stretch=False)
        self.friend_table.column('name', minwidth=30, width=120, stretch=False)
        self.friend_table.column(
            'status',
            minwidth=30,
            width=80,
            stretch=False
            )
        self.friend_table.column(
            'motherboard',
            minwidth=100,
            width=220,
            stretch=False
            )
        self.friend_table.column(
            'processor',
            minwidth=100,
            width=220,
            stretch=False
            )
        self.friend_table.grid(row=1, column=2, rowspan=5, sticky='nw')

        ttk.Label(self,
                  text='Добавить компьютер другу:').grid(
            row=2,
            column=0,
            padx=10,
            sticky='w'
            )

        self.comp_combo = ttk.Combobox(self, textvariable=self.comp_var)
        self.comp_combo.configure(values=self.comp_item)
        self.comp_combo.grid(row=3, column=0, sticky='new', padx=10)
        ttk.Button(
            self,
            text='Добавить',
            command=self.add_comp_to_friend).grid(
            row=3,
            column=1,
            sticky='nw'
            )

        ttk.Label(
            self,
            textvariable=self.error,
            foreground=ERROR).grid(row=4, column=0, columnspan=2)
        ttk.Label(
            self,
            textvariable=self.success,
            foreground=SUCCESS).grid(row=5, column=0, columnspan=2)

        ttk.Button(
            self,
            text='Выйти из редактора',
            command=self.cancel).grid(row=6, column=0, sticky='n')
        ttk.Button(
            self,
            text='Удалить выбранный компьютер',
            command=self.delete_computer).grid(row=6, column=2, sticky='n')

        self.friend_combo.bind('<<ComboboxSelected>>', self.edit_friend)
        self.comp_combo.bind('<<ComboboxSelected>>', self.edit_comp)

    def delete_friend(self):
        """Удаляет запись о друге из БД."""
        if not self.validator.validate_id(self.friend_id):
            self.error.set('*Вы не выбрали друга')
            self.success.set('')
        else:
            self.error.set('')
            self.success.set('Друг успешно удален')
            self.friend_obj.delete(self.friend_id)
            self.friend_var.set('Выберите друга')
            self.comp_var.set('Выберите компьютер')
            self.friend_id = None
            self.update_table()
            self.update_combo()
            self.update_editor()
            main_window.insert_friends_data()

    def update_editor(self):
        """Обновляет таблицу друзей в окне режима редактора."""
        editor_window.__dict__['children']['!fulldataframes4'].delete_data()
        editor_window.__dict__['children']['!fulldataframes4'].insert_data()

    def delete_computer(self):
        """Удаляет запись в БД выбранного у друга компьютера."""
        for i in self.friend_table.selection():
            comp_id = self.friend_table.item(i)['values'][0]
            self.friend_comp_obj.delete_friend_computer(
                self.friend_id, comp_id
                )
            self.update_table()

    def update_combo(self):
        """Обновляет выпадающие списки для друга и его компьютера."""
        self.friend_combo['values'] = self.get_item()[0]
        self.comp_combo['values'] = self.get_item()[1]

    def add_comp_to_friend(self):
        """Добавляет компьютер другу."""
        computers_id = self.friend_comp_obj.get_particular_friend_computer(
            self.friend_id
            )
        ides = [i[0] for i in computers_id]
        if self.comp_id in ides:
            self.error.set('*Такой компьютер есть у этого друга')
            self.success.set('')
        else:
            self.friend_comp_obj.add_computer_to_friend(
                self.friend_id, self.comp_id
                )
            self.error.set('')
            self.success.set('Компьютер успешно добавлен другу')
            self.update_table()
            main_window.update_table()

    def update_table(self):
        """Обновляет таблицы в окне редактора друга."""
        self.clear_table(self.friend_table)
        computers_id = self.friend_comp_obj.get_particular_friend_computer(
            self.friend_id
            )
        for i in computers_id:
            if i[0] is None:
                continue
            else:
                data = self.get_full_info(self.comp_obj.read(i[0]))
                self.friend_table.insert(parent='', index=0, values=data)

    def edit_comp(self, event):
        """Устанавливает ID выбранного компьютера друга."""
        data = self.comp_combo.get().split()
        self.comp_id = int(data[0])

    def edit_friend(self, event):
        """Устанавливает ID выбранного друга."""
        data = self.friend_combo.get().split()
        self.friend_id = int(data[0])
        self.update_table()

    def get_full_info(self, data):
        """Возвращает информацию в удобном для пользователя виде."""
        lst = []
        lst.append(data[0])
        lst.append(data[1])
        lst.append(f'{"Неисправен" if data[2] == 0 else "Исправен"}')
        lst.append(f'{data[3]} {str(data[4])} МГц.')
        lst.append(f'{data[5]} {data[6]}')
        return lst

    def clear_table(self, table):
        """Удаляет все данные из таблицы."""
        for item in table.get_children():
            table.delete(item)

    def get_item(self):
        """Возвращает кортеж из записей из БД."""
        return (
            [i for i in self.friend_obj.read()],
            [i for i in self.comp_obj.read()]
            )

    def cancel(self):
        """Закрывает окно редактора друзей."""
        edit_friend_window.destroy()


if __name__ == '__main__':
    create_db()
    App('My Friends computers', WINDOW_SIZE)
