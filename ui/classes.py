import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame, QScrollArea, QAbstractItemView, QTabWidget, QDialog
from database.database import add_class, get_all_classes, update_class, delete_class, search_classes
from ui.class_subjects import ClassSubjectsWindow

class ClassesWindow(QWidget):

    def __init__(self, parent=None, container=None):
        super().__init__(container if container else parent)
        self.parent_window = parent
        self.embedded = container is not None
        self.selected_id = None
        if not self.embedded:
            self.setWindowTitle('Classes & Semesters - Smart Academic Timetable Management System')
            self.resize(1150, 720)
            self.setMinimumSize(1000, 650)
        self.setup_ui()
        self.load_classes()
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
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        lbl_title = QLabel('Classes')
        lbl_title.setStyleSheet('font-size: 22px; font-weight: bold;')
        lbl_sub = QLabel('Manage classes and student sections')
        lbl_sub.setProperty('secondary', True)
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        btn_assign_subjects = QPushButton('Assign Subjects')
        btn_assign_subjects.setProperty('btnStyle', 'secondary')
        btn_assign_subjects.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_assign_subjects.clicked.connect(self.open_class_subjects_modal)
        header_layout.addWidget(btn_assign_subjects)
        main_layout.addWidget(header_card)
        form_card = QFrame()
        form_card.setObjectName('Card')
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(25, 20, 25, 25)
        form_layout.setSpacing(15)
        form_title = QLabel('Class Info')
        form_title.setStyleSheet('font-size: 16px; font-weight: bold;')
        form_layout.addWidget(form_title)
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)
        lbl_cname = QLabel('Class Name *')
        lbl_cname.setStyleSheet('font-weight: 600;')
        self.class_name_entry = QLineEdit()
        self.class_name_entry.setPlaceholderText('e.g. BCA 1st Year')
        grid.addWidget(lbl_cname, 0, 0)
        grid.addWidget(self.class_name_entry, 1, 0)
        lbl_dept = QLabel('Department *')
        lbl_dept.setStyleSheet('font-weight: 600;')
        self.dept_entry = QLineEdit()
        self.dept_entry.setPlaceholderText('e.g. BCA')
        grid.addWidget(lbl_dept, 0, 1)
        grid.addWidget(self.dept_entry, 1, 1)
        lbl_sem = QLabel('Semester *')
        lbl_sem.setStyleSheet('font-weight: 600;')
        self.sem_combo = QComboBox()
        self.sem_combo.addItems([str(i) for i in range(1, 9)])
        grid.addWidget(lbl_sem, 0, 2)
        grid.addWidget(self.sem_combo, 1, 2)
        lbl_ayear = QLabel('Academic Year')
        lbl_ayear.setStyleSheet('font-weight: 600;')
        self.academic_year_entry = QLineEdit('2024-2025')
        self.academic_year_entry.setPlaceholderText('2024-2025')
        grid.addWidget(lbl_ayear, 0, 3)
        grid.addWidget(self.academic_year_entry, 1, 3)
        form_layout.addLayout(grid)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.btn_add = QPushButton('Add')
        self.btn_add.setProperty('btnStyle', 'success')
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.add_class_record)
        btn_layout.addWidget(self.btn_add)
        self.btn_update = QPushButton('Update')
        self.btn_update.setProperty('btnStyle', 'secondary')
        self.btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_update.clicked.connect(self.update_class_record)
        btn_layout.addWidget(self.btn_update)
        self.btn_delete = QPushButton('Delete')
        self.btn_delete.setProperty('btnStyle', 'danger')
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_class_record)
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
        lbl_tbl_title = QLabel('Classes')
        lbl_tbl_title.setStyleSheet('font-size: 16px; font-weight: bold;')
        search_layout.addWidget(lbl_tbl_title)
        search_layout.addStretch()
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText('Search classes...')
        self.search_entry.setFixedWidth(260)
        self.search_entry.textChanged.connect(self.search_records)
        search_layout.addWidget(self.search_entry)
        btn_reset = QPushButton('Reset')
        btn_reset.setProperty('btnStyle', 'secondary')
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.clicked.connect(lambda: [self.search_entry.clear(), self.load_classes()])
        search_layout.addWidget(btn_reset)
        table_layout.addLayout(search_layout)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', 'Class Name', 'Department', 'Semester', 'Academic Year'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setMinimumHeight(300)
        self.table.itemSelectionChanged.connect(self.on_table_select)
        table_layout.addWidget(self.table)
        main_layout.addWidget(table_card)
        main_layout.addStretch()

    def load_classes(self, records=None):
        if records is None:
            records = get_all_classes() or []
        self.records_data = records
        self.table.setRowCount(0)
        for row_idx, rec in enumerate(records):
            self.table.insertRow(row_idx)
            for col_idx in range(min(5, len(rec))):
                val = rec[col_idx]
                item = QTableWidgetItem(str(val) if val is not None else '')
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if col_idx in [0, 3] else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_idx, col_idx, item)

    def on_table_select(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        row = selected_items[0].row()
        if row < len(self.records_data):
            rec = self.records_data[row]
            self.selected_id = rec[0]
            self.class_name_entry.setText(str(rec[1] or ''))
            self.dept_entry.setText(str(rec[2] or ''))
            self.sem_combo.setCurrentText(str(rec[3] or '1'))
            self.academic_year_entry.setText(str(rec[4] or '2024-2025'))

    def clear_form(self):
        self.selected_id = None
        self.class_name_entry.clear()
        self.dept_entry.clear()
        self.sem_combo.setCurrentIndex(0)
        self.academic_year_entry.setText('2024-2025')
        self.table.clearSelection()

    def validate_inputs(self):
        cname = self.class_name_entry.text().strip()
        dept = self.dept_entry.text().strip()
        if not cname:
            QMessageBox.warning(self, 'Validation Error', 'Class Name is required.')
            self.class_name_entry.setFocus()
            return False
        if not dept:
            QMessageBox.warning(self, 'Validation Error', 'Department is required.')
            self.dept_entry.setFocus()
            return False
        return True

    def add_class_record(self):
        if not self.validate_inputs():
            return
        cname = self.class_name_entry.text().strip()
        dept = self.dept_entry.text().strip()
        sem = self.sem_combo.currentText()
        ayear = self.academic_year_entry.text().strip() or '2024-2025'
        success = add_class(class_name=cname, department=dept, semester=sem, academic_year=ayear)
        if success:
            QMessageBox.information(self, 'Success', 'Class created successfully!')
            self.clear_form()
            self.load_classes()
        else:
            QMessageBox.critical(self, 'Error', 'Failed to add class.')

    def update_class_record(self):
        if not self.selected_id:
            QMessageBox.warning(self, 'Update', 'Please select a class from the table to update.')
            return
        if not self.validate_inputs():
            return
        cname = self.class_name_entry.text().strip()
        dept = self.dept_entry.text().strip()
        sem = self.sem_combo.currentText()
        ayear = self.academic_year_entry.text().strip() or '2024-2025'
        success = update_class(record_id=self.selected_id, class_name=cname, department=dept, semester=sem, academic_year=ayear)
        if success:
            QMessageBox.information(self, 'Success', 'Class updated successfully!')
            self.clear_form()
            self.load_classes()
        else:
            QMessageBox.critical(self, 'Error', 'Failed to update class.')

    def delete_class_record(self):
        if not self.selected_id:
            QMessageBox.warning(self, 'Delete', 'Please select a class from the table to delete.')
            return
        confirm = QMessageBox.question(self, 'Confirm Delete', f"Are you sure you want to delete '{self.class_name_entry.text().strip()}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            success = delete_class(self.selected_id)
            if success:
                QMessageBox.information(self, 'Deleted', 'Class deleted successfully.')
                self.clear_form()
                self.load_classes()
            else:
                QMessageBox.critical(self, 'Error', 'Failed to delete class.')

    def open_class_subjects_modal(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Class Subjects')
        dialog.resize(1100, 680)
        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        ClassSubjectsWindow(dialog, preselected_class_id=self.selected_id, container=dialog)
        dialog.exec()

    def search_records(self, text):
        query = text.strip()
        if not query:
            self.load_classes()
        else:
            records = search_classes(query) or []
            self.load_classes(records)
if __name__ == '__main__':
    from database.database import create_tables
    from ui.theme import apply_theme
    create_tables()
    app = QApplication.instance() or QApplication(sys.argv)
    apply_theme()
    win = ClassesWindow()
    win.show()
    sys.exit(app.exec())
