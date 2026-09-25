import re
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame, QScrollArea, QAbstractItemView, QSizePolicy
from database.database import add_faculty, get_all_faculty, update_faculty, delete_faculty, search_faculty

class FacultyWindow(QWidget):

    def __init__(self, parent=None, container=None, navigate=None):
        super().__init__(container if container else parent)
        self.parent_window = parent
        self.navigate = navigate
        self.embedded = container is not None
        self.selected_id = None
        if not self.embedded:
            self.setWindowTitle('Faculty Management - Smart Academic Timetable Management System')
            self.resize(1200, 720)
            self.setMinimumSize(1050, 650)
        self.setup_ui()
        self.load_faculty()
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
        lbl_title = QLabel('Faculty')
        lbl_title.setStyleSheet('font-size: 22px; font-weight: bold;')
        lbl_sub = QLabel('Manage faculty members and teaching hours')
        lbl_sub.setProperty('secondary', True)
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        if self.navigate:
            btn_workload = QPushButton('Workload')
            btn_workload.setProperty('btnStyle', 'secondary')
            btn_workload.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_workload.clicked.connect(lambda: self.navigate('assignments'))
            header_layout.addWidget(btn_workload)
        main_layout.addWidget(header_card)
        form_card = QFrame()
        form_card.setObjectName('Card')
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(25, 20, 25, 25)
        form_layout.setSpacing(15)
        form_title = QLabel('Faculty Info')
        form_title.setStyleSheet('font-size: 16px; font-weight: bold;')
        form_layout.addWidget(form_title)
        grid = QGridLayout()
        grid.setSpacing(14)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        lbl_fid = QLabel('Faculty ID')
        lbl_fid.setStyleSheet('font-weight: 600;')
        self.faculty_id_entry = QLineEdit()
        self.faculty_id_entry.setPlaceholderText('e.g. FAC001')
        grid.addWidget(lbl_fid, 0, 0)
        grid.addWidget(self.faculty_id_entry, 1, 0)
        lbl_fname = QLabel('Name *')
        lbl_fname.setStyleSheet('font-weight: 600;')
        self.name_entry = QLineEdit()
        self.name_entry.setPlaceholderText('Enter name')
        grid.addWidget(lbl_fname, 0, 1)
        grid.addWidget(self.name_entry, 1, 1)
        lbl_dept = QLabel('Department *')
        lbl_dept.setStyleSheet('font-weight: 600;')
        self.department_entry = QLineEdit()
        self.department_entry.setPlaceholderText('e.g. BCA')
        grid.addWidget(lbl_dept, 2, 0)
        grid.addWidget(self.department_entry, 3, 0)
        lbl_email = QLabel('Email')
        lbl_email.setStyleSheet('font-weight: 600;')
        self.email_entry = QLineEdit()
        self.email_entry.setPlaceholderText('name@college.edu')
        grid.addWidget(lbl_email, 2, 1)
        grid.addWidget(self.email_entry, 3, 1)
        lbl_phone = QLabel('Phone')
        lbl_phone.setStyleSheet('font-weight: 600;')
        self.phone_entry = QLineEdit()
        self.phone_entry.setPlaceholderText('e.g. 9876543210')
        grid.addWidget(lbl_phone, 4, 0)
        grid.addWidget(self.phone_entry, 5, 0)
        form_layout.addLayout(grid)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.btn_add = QPushButton('Add')
        self.btn_add.setProperty('btnStyle', 'success')
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.add_faculty_record)
        btn_layout.addWidget(self.btn_add)
        self.btn_update = QPushButton('Update')
        self.btn_update.setProperty('btnStyle', 'secondary')
        self.btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_update.clicked.connect(self.update_faculty_record)
        btn_layout.addWidget(self.btn_update)
        self.btn_delete = QPushButton('Delete')
        self.btn_delete.setProperty('btnStyle', 'danger')
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_faculty_record)
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
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        lbl_tbl_title = QLabel('Faculty List')
        lbl_tbl_title.setStyleSheet('font-size: 16px; font-weight: bold;')
        search_layout.addWidget(lbl_tbl_title)
        search_layout.addStretch()
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText('Search faculty...')
        self.search_entry.setFixedWidth(260)
        self.search_entry.textChanged.connect(self.search_records)
        search_layout.addWidget(self.search_entry)
        btn_reset = QPushButton('Reset')
        btn_reset.setProperty('btnStyle', 'secondary')
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.clicked.connect(lambda: [self.search_entry.clear(), self.load_faculty()])
        search_layout.addWidget(btn_reset)
        table_layout.addLayout(search_layout)
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['ID', 'Faculty ID', 'Name', 'Department', 'Email', 'Phone'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setMinimumHeight(300)
        self.table.itemSelectionChanged.connect(self.on_table_select)
        table_layout.addWidget(self.table)
        main_layout.addWidget(table_card)
        main_layout.addStretch()

    def load_faculty(self, records=None):
        if records is None:
            records = get_all_faculty() or []
        self.records_data = records
        self.table.setRowCount(0)
        for row_idx, rec in enumerate(records):
            self.table.insertRow(row_idx)
            for col_idx in range(min(6, len(rec))):
                val = rec[col_idx]
                item = QTableWidgetItem(str(val) if val is not None else '')
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if col_idx in [0, 1] else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_idx, col_idx, item)

    def on_table_select(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        row = selected_items[0].row()
        if row < len(self.records_data):
            rec = self.records_data[row]
            self.selected_id = rec[0]
            self.faculty_id_entry.setText(str(rec[1] or ''))
            self.name_entry.setText(str(rec[2] or ''))
            self.department_entry.setText(str(rec[3] or ''))
            self.email_entry.setText(str(rec[4] or ''))
            self.phone_entry.setText(str(rec[5] or ''))

    def clear_form(self):
        self.selected_id = None
        self.faculty_id_entry.clear()
        self.name_entry.clear()
        self.department_entry.clear()
        self.email_entry.clear()
        self.phone_entry.clear()
        self.table.clearSelection()

    def validate_inputs(self):
        name = self.name_entry.text().strip()
        dept = self.department_entry.text().strip()
        email = self.email_entry.text().strip()
        phone = self.phone_entry.text().strip()
        if not name:
            QMessageBox.warning(self, 'Validation Error', 'Faculty Name is required.')
            self.name_entry.setFocus()
            return False
        if not dept:
            QMessageBox.warning(self, 'Validation Error', 'Department is required.')
            self.department_entry.setFocus()
            return False
        if email and (not re.match('^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$', email)):
            QMessageBox.warning(self, 'Validation Error', 'Please enter a valid email address.')
            self.email_entry.setFocus()
            return False
        if phone and (not re.match('^[0-9+\\-()\\s]{7,15}$', phone)):
            QMessageBox.warning(self, 'Validation Error', 'Please enter a valid phone number.')
            self.phone_entry.setFocus()
            return False
        return True

    def add_faculty_record(self):
        if not self.validate_inputs():
            return
        fid = self.faculty_id_entry.text().strip()
        name = self.name_entry.text().strip()
        dept = self.department_entry.text().strip()
        email = self.email_entry.text().strip()
        phone = self.phone_entry.text().strip()
        success = add_faculty(faculty_id=fid, name=name, department=dept, email=email, phone=phone)
        if success:
            QMessageBox.information(self, 'Success', 'Faculty added successfully!')
            self.clear_form()
            self.load_faculty()
        else:
            QMessageBox.critical(self, 'Error', 'Failed to add faculty. Faculty ID may already exist.')

    def update_faculty_record(self):
        if not self.selected_id:
            QMessageBox.warning(self, 'Update', 'Please select a faculty member from the table to update.')
            return
        if not self.validate_inputs():
            return
        fid = self.faculty_id_entry.text().strip()
        name = self.name_entry.text().strip()
        dept = self.department_entry.text().strip()
        email = self.email_entry.text().strip()
        phone = self.phone_entry.text().strip()
        success = update_faculty(record_id=self.selected_id, faculty_id=fid, name=name, department=dept, email=email, phone=phone)
        if success:
            QMessageBox.information(self, 'Success', 'Faculty updated successfully!')
            self.clear_form()
            self.load_faculty()
        else:
            QMessageBox.critical(self, 'Error', 'Failed to update faculty.')

    def delete_faculty_record(self):
        if not self.selected_id:
            QMessageBox.warning(self, 'Delete', 'Please select a faculty member from the table to delete.')
            return
        confirm = QMessageBox.question(self, 'Confirm Delete', f"Are you sure you want to delete '{self.name_entry.text().strip()}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            success, msg = delete_faculty(self.selected_id)
            if success:
                QMessageBox.information(self, 'Deleted', 'Faculty deleted successfully.')
                self.clear_form()
                self.load_faculty()
            else:
                QMessageBox.critical(self, 'Error', f'Failed to delete faculty:\n{msg}')

    def search_records(self, text):
        query = text.strip()
        if not query:
            self.load_faculty()
        else:
            records = search_faculty(query) or []
            self.load_faculty(records)
if __name__ == '__main__':
    from database.database import create_tables
    from ui.theme import apply_theme
    create_tables()
    app = QApplication.instance() or QApplication(sys.argv)
    apply_theme()
    win = FacultyWindow()
    win.show()
    sys.exit(app.exec())
