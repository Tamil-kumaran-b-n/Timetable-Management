import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame, QScrollArea, QAbstractItemView
from database.database import get_all_faculty, get_all_classes, get_all_subjects
from database.workload import add_workload, get_all_workloads, update_workload, delete_workload

class AssignmentsWindow(QWidget):

    def __init__(self, parent=None, preselected_faculty_id=None, container=None):
        super().__init__(container if container else parent)
        self.parent_window = parent
        self.embedded = container is not None
        self.preselected_faculty_id = preselected_faculty_id
        self.selected_workload_id = None
        self.faculty_records = []
        self.class_records = []
        self.subject_records = []
        if not self.embedded:
            self.setWindowTitle('Faculty Workload Management - Smart Academic Timetable Management System')
            self.resize(1150, 720)
            self.setMinimumSize(1000, 650)
        self.setup_ui()
        self.load_dropdowns()
        self.load_workloads()
        if container:
            container_layout = container.layout()
            if container_layout:
                container_layout.addWidget(self)

    def setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        root_layout.addWidget(scroll)
        scroll_content = QWidget()
        scroll_content.setObjectName('ScrollContent')
        scroll.setWidget(scroll_content)
        main_layout = QVBoxLayout(scroll_content)
        main_layout.setContentsMargins(30, 25, 30, 30)
        main_layout.setSpacing(20)
        header_card = QFrame()
        header_card.setObjectName('Card')
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(25, 18, 25, 18)
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        lbl_title = QLabel('Workload')
        lbl_title.setStyleSheet('font-size: 22px; font-weight: bold;')
        lbl_sub = QLabel('Assign subjects and teaching periods to faculty')
        lbl_sub.setProperty('secondary', True)
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        main_layout.addWidget(header_card)
        form_card = QFrame()
        form_card.setObjectName('Card')
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(25, 20, 25, 25)
        form_layout.setSpacing(15)
        form_title = QLabel('Assign Workload')
        form_title.setStyleSheet('font-size: 16px; font-weight: bold;')
        form_layout.addWidget(form_title)
        grid = QGridLayout()
        grid.setSpacing(14)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)
        lbl_fac = QLabel('Faculty *')
        lbl_fac.setStyleSheet('font-weight: 600;')
        self.faculty_combo = QComboBox()
        grid.addWidget(lbl_fac, 0, 0)
        grid.addWidget(self.faculty_combo, 1, 0)
        lbl_cls = QLabel('Class *')
        lbl_cls.setStyleSheet('font-weight: 600;')
        self.class_combo = QComboBox()
        grid.addWidget(lbl_cls, 0, 1)
        grid.addWidget(self.class_combo, 1, 1)
        lbl_sub = QLabel('Subject *')
        lbl_sub.setStyleSheet('font-weight: 600;')
        self.subject_combo = QComboBox()
        grid.addWidget(lbl_sub, 0, 2)
        grid.addWidget(self.subject_combo, 1, 2)
        lbl_periods = QLabel('Periods/Week *')
        lbl_periods.setStyleSheet('font-weight: 600;')
        self.periods_entry = QLineEdit('4')
        self.periods_entry.setPlaceholderText('4')
        grid.addWidget(lbl_periods, 0, 3)
        grid.addWidget(self.periods_entry, 1, 3)
        form_layout.addLayout(grid)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.btn_add = QPushButton('Assign')
        self.btn_add.setProperty('btnStyle', 'success')
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.add_workload_record)
        btn_layout.addWidget(self.btn_add)
        self.btn_update = QPushButton('Update')
        self.btn_update.setProperty('btnStyle', 'secondary')
        self.btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_update.clicked.connect(self.update_workload_record)
        btn_layout.addWidget(self.btn_update)
        self.btn_delete = QPushButton('Delete')
        self.btn_delete.setProperty('btnStyle', 'danger')
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_workload_record)
        btn_layout.addWidget(self.btn_delete)
        self.btn_clear = QPushButton('Clear')
        self.btn_clear.setProperty('btnStyle', 'ghost')
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.clicked.connect(self.clear_form)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        form_layout.addLayout(btn_layout)
        main_layout.addWidget(form_card)
        table_card = QFrame()
        table_card.setObjectName('Card')
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(25, 20, 25, 25)
        table_layout.setSpacing(15)
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        lbl_tbl = QLabel('Workload List')
        lbl_tbl.setStyleSheet('font-size: 16px; font-weight: bold;')
        filter_layout.addWidget(lbl_tbl)
        filter_layout.addStretch()
        filter_layout.addWidget(QLabel('Faculty:'))
        self.filter_faculty_combo = QComboBox()
        self.filter_faculty_combo.setMinimumWidth(220)
        self.filter_faculty_combo.currentIndexChanged.connect(self.filter_table_by_faculty)
        filter_layout.addWidget(self.filter_faculty_combo)
        btn_show_all = QPushButton('Show All')
        btn_show_all.setProperty('btnStyle', 'secondary')
        btn_show_all.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_show_all.clicked.connect(lambda: self.filter_faculty_combo.setCurrentIndex(0))
        filter_layout.addWidget(btn_show_all)
        table_layout.addLayout(filter_layout)
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['ID', 'Faculty Name', 'Class Name', 'Semester', 'Subject Code', 'Subject Name', 'Hrs / Wk'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setMinimumHeight(300)
        self.table.itemSelectionChanged.connect(self.on_table_select)
        table_layout.addWidget(self.table)
        main_layout.addWidget(table_card)
        main_layout.addStretch()

    def load_dropdowns(self):
        self.faculty_records = get_all_faculty() or []
        self.faculty_combo.clear()
        self.filter_faculty_combo.clear()
        self.filter_faculty_combo.addItem('All Faculty Members', None)
        selected_idx = 0
        for idx, f in enumerate(self.faculty_records):
            fid = f[0]
            fname = f[2]
            dept = f[3] if len(f) > 3 else ''
            display = f'{fname} ({dept})'
            self.faculty_combo.addItem(display, fid)
            self.filter_faculty_combo.addItem(display, fid)
            if self.preselected_faculty_id and fid == self.preselected_faculty_id:
                selected_idx = idx
        if self.faculty_records:
            self.faculty_combo.setCurrentIndex(selected_idx)
        self.class_records = get_all_classes() or []
        self.class_combo.clear()
        for c in self.class_records:
            cid = c[0]
            cname = c[1]
            sem = c[3] if len(c) > 3 else ''
            self.class_combo.addItem(f'{cname} (Sem {sem})', cid)
        self.subject_records = get_all_subjects() or []
        self.subject_combo.clear()
        for s in self.subject_records:
            sid = s[0]
            code = s[1]
            sname = s[2]
            self.subject_combo.addItem(f'{code} - {sname}', sid)

    def load_workloads(self, records=None):
        if records is None:
            records = get_all_workloads() or []
        self.records_data = records
        self.table.setRowCount(0)
        for row_idx, rec in enumerate(records):
            self.table.insertRow(row_idx)
            wid = rec[0] if len(rec) > 0 else ''
            fname = rec[3] if len(rec) > 3 else ''
            cname = rec[5] if len(rec) > 5 else ''
            sem = f'Sem {rec[7]}' if len(rec) > 7 and rec[7] else '—'
            scode = rec[10] if len(rec) > 10 else ''
            sname = rec[11] if len(rec) > 11 else ''
            hrs = rec[13] if len(rec) > 13 else ''
            row_items = [str(wid), str(fname), str(cname), str(sem), str(scode), str(sname), str(hrs)]
            for col_idx, text in enumerate(row_items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if col_idx in [0, 3, 4, 6] else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_idx, col_idx, item)

    def filter_table_by_faculty(self):
        selected_fid = self.filter_faculty_combo.currentData()
        all_wl = get_all_workloads() or []
        if selected_fid is None:
            self.load_workloads(all_wl)
        else:
            filtered = [w for w in all_wl if len(w) > 1 and w[1] == selected_fid]
            self.load_workloads(filtered)

    def on_table_select(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        row = selected_items[0].row()
        if row < len(self.records_data):
            rec = self.records_data[row]
            self.selected_workload_id = rec[0]
            fid = rec[1]
            cid = rec[4]
            sid = rec[9]
            hrs = rec[13] if len(rec) > 13 else 4
            for i in range(self.faculty_combo.count()):
                if self.faculty_combo.itemData(i) == fid:
                    self.faculty_combo.setCurrentIndex(i)
                    break
            for i in range(self.class_combo.count()):
                if self.class_combo.itemData(i) == cid:
                    self.class_combo.setCurrentIndex(i)
                    break
            for i in range(self.subject_combo.count()):
                if self.subject_combo.itemData(i) == sid:
                    self.subject_combo.setCurrentIndex(i)
                    break
            self.periods_entry.setText(str(hrs))

    def clear_form(self):
        self.selected_workload_id = None
        self.periods_entry.setText('4')
        self.table.clearSelection()

    def add_workload_record(self):
        faculty_id = self.faculty_combo.currentData()
        if not faculty_id:
            QMessageBox.warning(self, 'Validation Error', 'Please select a faculty member.')
            return
        class_id = self.class_combo.currentData()
        if not class_id:
            QMessageBox.warning(self, 'Validation Error', 'Please select an academic class.')
            return
        subject_id = self.subject_combo.currentData()
        if not subject_id:
            QMessageBox.warning(self, 'Validation Error', 'Please select a subject.')
            return
        try:
            hrs = int(self.periods_entry.text().strip())
            if hrs < 1 or hrs > 30:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, 'Validation Error', 'Periods/Week must be an integer between 1 and 30.')
            return
        workload_id = add_workload(faculty_id=faculty_id, class_id=class_id, subject_id=subject_id, priority='Normal', periods_per_week=hrs)
        if workload_id is not None:
            QMessageBox.information(self, 'Success', 'Faculty workload assigned successfully!')
            self.clear_form()
            self.load_workloads()
        else:
            QMessageBox.critical(self, 'Error', 'Failed to assign workload. This Faculty-Class-Subject combination already exists.')

    def update_workload_record(self):
        if not self.selected_workload_id:
            QMessageBox.warning(self, 'Update', 'Please select a workload record from the table to update.')
            return
        faculty_id = self.faculty_combo.currentData()
        class_id = self.class_combo.currentData()
        subject_id = self.subject_combo.currentData()
        try:
            hrs = int(self.periods_entry.text().strip())
            if hrs < 1 or hrs > 30:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, 'Validation Error', 'Periods/Week must be an integer between 1 and 30.')
            return
        success = update_workload(workload_id=self.selected_workload_id, faculty_id=faculty_id, class_id=class_id, subject_id=subject_id, priority='Normal', periods_per_week=hrs)
        if success:
            QMessageBox.information(self, 'Success', 'Workload updated successfully!')
            self.clear_form()
            self.load_workloads()
        else:
            QMessageBox.critical(self, 'Error', 'Failed to update workload.')

    def delete_workload_record(self):
        if not self.selected_workload_id:
            QMessageBox.warning(self, 'Delete', 'Please select a workload record from the table to delete.')
            return
        confirm = QMessageBox.question(self, 'Confirm Delete', 'Are you sure you want to remove this faculty workload assignment?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            success = delete_workload(self.selected_workload_id)
            if success:
                QMessageBox.information(self, 'Deleted', 'Workload deleted successfully.')
                self.clear_form()
                self.load_workloads()
            else:
                QMessageBox.critical(self, 'Error', 'Failed to delete workload.')
if __name__ == '__main__':
    from database.database import create_tables
    from ui.theme import apply_theme
    create_tables()
    app = QApplication.instance() or QApplication(sys.argv)
    apply_theme()
    win = AssignmentsWindow()
    win.show()
    sys.exit(app.exec())
