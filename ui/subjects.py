"""
Subject Management Window & Embedded Widget in PySide6.
"""

import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFrame, QScrollArea, QAbstractItemView
)

from database.database import (
    add_subject,
    get_all_subjects,
    update_subject,
    delete_subject,
    search_subjects
)


class SubjectsWindow(QWidget):
    def __init__(self, parent=None, container=None):
        super().__init__(container if container else parent)
        self.parent_window = parent
        self.embedded = container is not None
        self.selected_id = None

        if not self.embedded:
            self.setWindowTitle("Subject Management - Smart Academic Timetable Management System")
            self.resize(1200, 720)
            self.setMinimumSize(1050, 650)

        self.setup_ui()
        self.load_subjects()

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
        scroll_content.setObjectName("ScrollContent")
        scroll.setWidget(scroll_content)

        main_layout = QVBoxLayout(scroll_content)
        main_layout.setContentsMargins(30, 25, 30, 30)
        main_layout.setSpacing(20)

        # =====================================================
        # HEADER
        # =====================================================
        header_card = QFrame()
        header_card.setObjectName("Card")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(25, 18, 25, 18)

        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        lbl_title = QLabel("Subject Management")
        lbl_title.setStyleSheet("font-size: 22px; font-weight: bold;")
        lbl_sub = QLabel("Manage academic curriculum, theory subjects, practical labs, and required hours")
        lbl_sub.setProperty("secondary", True)
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        main_layout.addWidget(header_card)

        # =====================================================
        # FORM CARD
        # =====================================================
        form_card = QFrame()
        form_card.setObjectName("Card")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(25, 20, 25, 25)
        form_layout.setSpacing(15)

        form_title = QLabel("Subject Details")
        form_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        form_layout.addWidget(form_title)

        grid = QGridLayout()
        grid.setSpacing(14)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)

        # Row 0: Code, Name, Department, Semester
        lbl_code = QLabel("Subject Code *")
        lbl_code.setStyleSheet("font-weight: 600;")
        self.code_entry = QLineEdit()
        self.code_entry.setPlaceholderText("e.g. CS101")
        grid.addWidget(lbl_code, 0, 0)
        grid.addWidget(self.code_entry, 1, 0)

        lbl_name = QLabel("Subject Name *")
        lbl_name.setStyleSheet("font-weight: 600;")
        self.name_entry = QLineEdit()
        self.name_entry.setPlaceholderText("e.g. Data Structures & Algorithms")
        grid.addWidget(lbl_name, 0, 1)
        grid.addWidget(self.name_entry, 1, 1)

        lbl_dept = QLabel("Department *")
        lbl_dept.setStyleSheet("font-weight: 600;")
        self.dept_entry = QLineEdit()
        self.dept_entry.setPlaceholderText("e.g. BCA")
        grid.addWidget(lbl_dept, 0, 2)
        grid.addWidget(self.dept_entry, 1, 2)

        lbl_sem = QLabel("Semester *")
        lbl_sem.setStyleSheet("font-weight: 600;")
        self.sem_combo = QComboBox()
        self.sem_combo.addItems([str(i) for i in range(1, 9)])
        grid.addWidget(lbl_sem, 0, 3)
        grid.addWidget(self.sem_combo, 1, 3)

        # Row 1: Weekly Hours, Credits, Preferred Room Type, Is Lab / Lab duration
        lbl_hours = QLabel("Hours / Week *")
        lbl_hours.setStyleSheet("font-weight: 600;")
        self.hours_entry = QLineEdit("4")
        self.hours_entry.setPlaceholderText("4")
        grid.addWidget(lbl_hours, 2, 0)
        grid.addWidget(self.hours_entry, 3, 0)

        lbl_cred = QLabel("Credits")
        lbl_cred.setStyleSheet("font-weight: 600;")
        self.credits_entry = QLineEdit("3")
        self.credits_entry.setPlaceholderText("3")
        grid.addWidget(lbl_cred, 2, 1)
        grid.addWidget(self.credits_entry, 3, 1)

        lbl_room_type = QLabel("Preferred Room Type")
        lbl_room_type.setStyleSheet("font-weight: 600;")
        self.room_type_combo = QComboBox()
        self.room_type_combo.addItems(["Lecture Hall", "Computer Lab", "Science Lab", "Seminar Room", "Smart Classroom"])
        grid.addWidget(lbl_room_type, 2, 2)
        grid.addWidget(self.room_type_combo, 3, 2)

        # Lab details
        lab_layout = QHBoxLayout()
        lab_layout.setContentsMargins(0, 0, 0, 0)
        self.is_lab_check = QCheckBox("Is Lab")
        self.is_lab_check.toggled.connect(self.on_lab_toggle)
        lab_layout.addWidget(self.is_lab_check)

        self.lab_duration_combo = QComboBox()
        self.lab_duration_combo.addItems(["2 Hrs Block", "3 Hrs Block"])
        self.lab_duration_combo.setEnabled(False)
        lab_layout.addWidget(self.lab_duration_combo)

        lbl_lab = QLabel("Lab Settings")
        lbl_lab.setStyleSheet("font-weight: 600;")
        grid.addWidget(lbl_lab, 2, 3)
        grid.addLayout(lab_layout, 3, 3)

        form_layout.addLayout(grid)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_add = QPushButton("Add Subject")
        self.btn_add.setProperty("btnStyle", "success")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.add_subject_record)
        btn_layout.addWidget(self.btn_add)

        self.btn_update = QPushButton("Update Selected")
        self.btn_update.setProperty("btnStyle", "secondary")
        self.btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_update.clicked.connect(self.update_subject_record)
        btn_layout.addWidget(self.btn_update)

        self.btn_delete = QPushButton("Delete Selected")
        self.btn_delete.setProperty("btnStyle", "danger")
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_subject_record)
        btn_layout.addWidget(self.btn_delete)

        self.btn_clear = QPushButton("Clear Form")
        self.btn_clear.setProperty("btnStyle", "ghost")
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.clicked.connect(self.clear_form)
        btn_layout.addWidget(self.btn_clear)

        btn_layout.addStretch()
        form_layout.addLayout(btn_layout)

        main_layout.addWidget(form_card)

        # =====================================================
        # SEARCH & TABLE CARD
        # =====================================================
        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(25, 20, 25, 25)
        table_layout.setSpacing(15)

        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        lbl_tbl_title = QLabel("Subject Curriculum")
        lbl_tbl_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        search_layout.addWidget(lbl_tbl_title)
        search_layout.addStretch()

        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search code, name, department...")
        self.search_entry.setFixedWidth(260)
        self.search_entry.textChanged.connect(self.search_records)
        search_layout.addWidget(self.search_entry)

        btn_reset = QPushButton("Reset")
        btn_reset.setProperty("btnStyle", "secondary")
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.clicked.connect(lambda: [self.search_entry.clear(), self.load_subjects()])
        search_layout.addWidget(btn_reset)

        table_layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Code", "Subject Name", "Department", "Sem", "Credits", "Hours/Wk", "Lab", "Room Type"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setMinimumHeight(300)
        self.table.itemSelectionChanged.connect(self.on_table_select)

        table_layout.addWidget(self.table)
        main_layout.addWidget(table_card)
        main_layout.addStretch()

    def on_lab_toggle(self, checked):
        self.lab_duration_combo.setEnabled(checked)
        if checked and self.room_type_combo.currentText() == "Lecture Hall":
            self.room_type_combo.setCurrentText("Computer Lab")

    def load_subjects(self, records=None):
        if records is None:
            records = get_all_subjects() or []

        self.records_data = records
        self.table.setRowCount(0)

        for row_idx, rec in enumerate(records):
            self.table.insertRow(row_idx)
            for col_idx in range(min(9, len(rec))):
                val = rec[col_idx]
                if col_idx == 7:
                    val = "Yes" if val == 1 else "No"
                item = QTableWidgetItem(str(val) if val is not None else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if col_idx in [0, 1, 4, 5, 6, 7] else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_idx, col_idx, item)

    def on_table_select(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        if row < len(self.records_data):
            rec = self.records_data[row]
            self.selected_id = rec[0]
            self.code_entry.setText(str(rec[1] or ""))
            self.name_entry.setText(str(rec[2] or ""))
            self.dept_entry.setText(str(rec[3] or ""))
            self.sem_combo.setCurrentText(str(rec[4] or "1"))
            self.credits_entry.setText(str(rec[5] or "3"))
            self.hours_entry.setText(str(rec[6] or "4"))
            is_lab = bool(rec[7]) if len(rec) > 7 else False
            self.is_lab_check.setChecked(is_lab)
            if len(rec) > 8 and rec[8]:
                self.room_type_combo.setCurrentText(str(rec[8]))

    def clear_form(self):
        self.selected_id = None
        self.code_entry.clear()
        self.name_entry.clear()
        self.dept_entry.clear()
        self.sem_combo.setCurrentIndex(0)
        self.credits_entry.setText("3")
        self.hours_entry.setText("4")
        self.is_lab_check.setChecked(False)
        self.lab_duration_combo.setCurrentIndex(0)
        self.room_type_combo.setCurrentIndex(0)
        self.table.clearSelection()

    def validate_inputs(self):
        code = self.code_entry.text().strip()
        name = self.name_entry.text().strip()
        dept = self.dept_entry.text().strip()
        hours_str = self.hours_entry.text().strip()
        credits_str = self.credits_entry.text().strip()

        if not code:
            QMessageBox.warning(self, "Validation Error", "Subject Code is required.")
            self.code_entry.setFocus()
            return False

        if not name:
            QMessageBox.warning(self, "Validation Error", "Subject Name is required.")
            self.name_entry.setFocus()
            return False

        if not dept:
            QMessageBox.warning(self, "Validation Error", "Department is required.")
            self.dept_entry.setFocus()
            return False

        try:
            hours = int(hours_str)
            if hours < 1 or hours > 30:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Hours/Week must be an integer between 1 and 30.")
            self.hours_entry.setFocus()
            return False

        try:
            creds = int(credits_str)
            if creds < 0 or creds > 20:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Credits must be an integer between 0 and 20.")
            self.credits_entry.setFocus()
            return False

        return True

    def add_subject_record(self):
        if not self.validate_inputs():
            return

        code = self.code_entry.text().strip()
        name = self.name_entry.text().strip()
        dept = self.dept_entry.text().strip()
        sem = int(self.sem_combo.currentText())
        creds = int(self.credits_entry.text().strip())
        hours = int(self.hours_entry.text().strip())
        is_lab = 1 if self.is_lab_check.isChecked() else 0
        room_type = self.room_type_combo.currentText()

        success, msg = add_subject(
            subject_code=code,
            name=name,
            department=dept,
            semester=sem,
            credits=creds,
            hours_per_week=hours,
            is_lab=is_lab,
            preferred_room_type=room_type
        )

        if success:
            QMessageBox.information(self, "Success", "Subject added successfully!")
            self.clear_form()
            self.load_subjects()
        else:
            QMessageBox.critical(self, "Error", f"Failed to add subject:\n{msg}")

    def update_subject_record(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Update", "Please select a subject from the table to update.")
            return

        if not self.validate_inputs():
            return

        code = self.code_entry.text().strip()
        name = self.name_entry.text().strip()
        dept = self.dept_entry.text().strip()
        sem = int(self.sem_combo.currentText())
        creds = int(self.credits_entry.text().strip())
        hours = int(self.hours_entry.text().strip())
        is_lab = 1 if self.is_lab_check.isChecked() else 0
        room_type = self.room_type_combo.currentText()

        success, msg = update_subject(
            subject_db_id=self.selected_id,
            subject_code=code,
            name=name,
            department=dept,
            semester=sem,
            credits=creds,
            hours_per_week=hours,
            is_lab=is_lab,
            preferred_room_type=room_type
        )

        if success:
            QMessageBox.information(self, "Success", "Subject updated successfully!")
            self.clear_form()
            self.load_subjects()
        else:
            QMessageBox.critical(self, "Error", f"Failed to update subject:\n{msg}")

    def delete_subject_record(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Delete", "Please select a subject from the table to delete.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{self.name_entry.text().strip()}' ({self.code_entry.text().strip()})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            success, msg = delete_subject(self.selected_id)
            if success:
                QMessageBox.information(self, "Deleted", "Subject deleted successfully.")
                self.clear_form()
                self.load_subjects()
            else:
                QMessageBox.critical(self, "Error", f"Failed to delete subject:\n{msg}")

    def search_records(self, text):
        query = text.strip()
        if not query:
            self.load_subjects()
        else:
            records = search_subjects(query) or []
            self.load_subjects(records)


if __name__ == "__main__":
    from database.database import create_tables
    from ui.theme import apply_theme

    create_tables()
    app = QApplication.instance() or QApplication(sys.argv)
    apply_theme()
    win = SubjectsWindow()
    win.show()
    sys.exit(app.exec())
