import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QTabWidget, QAbstractScrollArea,
                             QVBoxLayout, QHBoxLayout, QTableWidget, QGroupBox,
                             QTableWidgetItem, QPushButton, QMessageBox)
from helper_func import weekday

names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self._connect_to_db()

        self.setWindowTitle("schedule")

        self.vbox = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        self.vbox.addWidget(self.tabs)

        for i in range(6):
            self._create_day_tab(names[i])

        self._create_teacher_tab('teacher')


    def _connect_to_db(self):
        self.conn = psycopg2.connect(database="schedule_bot", user="dbadmin",
                                     password="pass", host="localhost", port="5434")
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.conn.cursor()

    def _create_day_tab(self, name):
        setattr(self, name+'_tab', QWidget())
        current_tab = getattr(self, name+'_tab')
        self.tabs.addTab(current_tab, name)

        setattr(self, name+'_gbox', QGroupBox(name))

        setattr(self, name+'_svbox', QVBoxLayout())
        setattr(self, name+'_shbox1', QHBoxLayout())
        setattr(self, name+'_shbox2', QHBoxLayout())

        current_svbox = getattr(self, name+'_svbox')
        current_shbox1 = getattr(self, name+'_shbox1')
        current_shbox2 = getattr(self, name+'_shbox2')

        current_svbox.addLayout(current_shbox1)
        current_svbox.addLayout(current_shbox2)

        current_shbox1.addWidget(getattr(self, name+'_gbox'))
        self._create_day_table(name)

        setattr(self, f'update_{name}_button', QPushButton("Update"))
        current_update_button = getattr(self, f'update_{name}_button')
        current_shbox2.addWidget(current_update_button)
        current_update_button.clicked.connect(self._update_schedule)

        current_tab.setLayout(current_svbox)

    def _create_day_table(self, name):
        setattr(self, name+'_table', QTableWidget())
        current_table = getattr(self, name+'_table')
        current_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        current_table.setColumnCount(6)
        current_table.setHorizontalHeaderLabels(["Subject", "Subject type", "Room Number", "Start time", " ", " "])

        self._update_day_table(name)

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(current_table)
        current_box = getattr(self, name+'_gbox')
        current_box.setLayout(self.mvbox)

    def _update_day_table(self, name):
        self.cursor.execute(f"SELECT * FROM public.timetable WHERE day={weekday(name)} ORDER BY start_time ASC")
        records = list(self.cursor.fetchall())
        current_table = getattr(self, name+'_table')
        current_table.setRowCount(len(records)+1)
        join_button = []
        delete_button = []

        for (i, r) in enumerate(records):
            r = list(r)
            join_button.append(QPushButton("Join"))
            delete_button.append(QPushButton("Delete"))
            current_table.setItem(i, 0, QTableWidgetItem(str(r[2])))
            current_table.setItem(i, 1, QTableWidgetItem(str(r[3])))
            current_table.setItem(i, 2, QTableWidgetItem(str(r[4])))
            current_table.setItem(i, 3, QTableWidgetItem(str(r[5])))
            current_table.setCellWidget(i, 4, join_button[i])
            current_table.setCellWidget(i, 5, delete_button[i])
            join_button[i].clicked.connect(lambda _, n1=i, day=name, id=r[0], d=False: self._change_day_from_table(n1, day, id, d))
            delete_button[i].clicked.connect(lambda _, n1=i, day=name, id=r[0], d=True: self._change_day_from_table(n1, day, id, d))

        i += 1
        join_button.append(QPushButton("Join"))
        current_table.setItem(i, 0, QTableWidgetItem(None))
        current_table.setItem(i, 1, QTableWidgetItem(None))
        current_table.setItem(i, 2, QTableWidgetItem(None))
        current_table.setItem(i, 3, QTableWidgetItem(None))
        current_table.setCellWidget(i, 4, join_button[i])
        join_button[i].clicked.connect(lambda _, n1=i, day=name, id='new', d=False: self._change_day_from_table(n1, day, id, d))

        current_table.resizeRowsToContents()

    def _change_day_from_table(self, row_num, day, id, d):
        row = []
        current_table = getattr(self, day+'_table')
        if d:
            self.cursor.execute(f"DELETE FROM public.timetable WHERE id={id}")
        else:
            for i in range(current_table.columnCount()):
                try:
                    row.append(current_table.item(row_num, i).text())
                except:
                    row.append(None)

            try:
                if id != 'new':
                    self.cursor.execute(f"UPDATE public.timetable SET subject='{row[0]}', s_type={int(row[1])}, \
                                        room_numb='{row[2]}', start_time={int(row[3])} WHERE id={int(id)}")
                else:
                    self.cursor.execute(f"INSERT INTO public.timetable (day, subject, s_type, room_numb, start_time) \
                                        VALUES ({weekday(day)}, '{row[0]}', {int(row[1])}, '{row[2]}', {int(row[3])})")
            except:
                QMessageBox.about(self, "Error", "Enter all fields")

    def _update_schedule(self):
        for i in range(6):
            self._update_day_table(names[i])
        self._update_teacher_table('teacher')

    def _create_teacher_tab(self, name):
        setattr(self, name + '_tab', QWidget())
        current_tab = getattr(self, name + '_tab')
        self.tabs.addTab(current_tab, name)

        setattr(self, name + '_gbox', QGroupBox(name))

        setattr(self, name + '_svbox', QVBoxLayout())
        setattr(self, name + '_shbox1', QHBoxLayout())
        setattr(self, name + '_shbox2', QHBoxLayout())

        current_svbox = getattr(self, name + '_svbox')
        current_shbox1 = getattr(self, name + '_shbox1')
        current_shbox2 = getattr(self, name + '_shbox2')

        current_svbox.addLayout(current_shbox1)
        current_svbox.addLayout(current_shbox2)

        current_shbox1.addWidget(getattr(self, name + '_gbox'))
        self._create_teacher_table(name)

        setattr(self, f'update_{name}_button', QPushButton("Update"))
        current_update_button = getattr(self, f'update_{name}_button')
        current_shbox2.addWidget(current_update_button)
        current_update_button.clicked.connect(self._update_schedule)

        current_tab.setLayout(current_svbox)

    def _create_teacher_table(self, name):
        setattr(self, name+'_table', QTableWidget())
        current_table = getattr(self, name+'_table')
        current_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        current_table.setColumnCount(5)
        current_table.setHorizontalHeaderLabels(["Full name", "Subject", "Subject type", " ", " "])

        self._update_teacher_table(name)

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(current_table)
        current_box = getattr(self, name+'_gbox')
        current_box.setLayout(self.mvbox)

    def _update_teacher_table(self, name):
        self.cursor.execute(f"SELECT * FROM public.teacher ORDER BY subject ASC")
        records = list(self.cursor.fetchall())
        current_table = getattr(self, name+'_table')
        current_table.setRowCount(len(records)+1)
        join_button = []
        delete_button = []

        for (i, r) in enumerate(records):
            r = list(r)
            join_button.append(QPushButton("Join"))
            delete_button.append(QPushButton("Delete"))
            current_table.setItem(i, 0, QTableWidgetItem(str(r[1])))
            current_table.setItem(i, 1, QTableWidgetItem(str(r[2])))
            current_table.setItem(i, 2, QTableWidgetItem(str(r[3])))
            current_table.setCellWidget(i, 3, join_button[i])
            current_table.setCellWidget(i, 4, delete_button[i])
            join_button[i].clicked.connect(lambda _, n1=i, day='teacher', id=r[0], d=False: self._change_teacher_from_table(n1, day, id, d))
            delete_button[i].clicked.connect(lambda _, n1=i, day='teacher', id=r[0], d=True: self._change_teacher_from_table(n1, day, id, d))

        i += 1
        join_button.append(QPushButton("Join"))
        current_table.setItem(i, 0, QTableWidgetItem(None))
        current_table.setItem(i, 1, QTableWidgetItem(None))
        current_table.setItem(i, 2, QTableWidgetItem(None))
        current_table.setCellWidget(i, 3, join_button[i])
        join_button[i].clicked.connect(lambda _, n1=i, day='teacher', id='new', d=False: self._change_teacher_from_table(n1, day, id, d))

        current_table.resizeRowsToContents()

    def _change_teacher_from_table(self, row_num, day, id, d):
        row = []
        current_table = getattr(self, day+'_table')
        if d:
            self.cursor.execute(f"DELETE FROM public.timetable WHERE id={id}")
        else:
            for i in range(current_table.columnCount()):
                try:
                    row.append(current_table.item(row_num, i).text())
                except:
                    row.append(None)
            try:
                if id != 'new':
                    self.cursor.execute(f"UPDATE public.teacher SET full_name='{row[0]}', subject='{row[1]}', \
                                        s_type={int(row[2])} WHERE id={int(id)}")
                else:
                    self.cursor.execute(f"INSERT INTO public.teacher (full_name, subject, s_type) \
                                        VALUES ('{row[0]}', '{row[1]}', {row[2]})")
            except:
                QMessageBox.about(self, "Error", "Enter all fields")


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())
