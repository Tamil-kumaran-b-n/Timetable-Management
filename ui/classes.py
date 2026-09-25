"""
Classes & Semesters Management Window & Embedded Widget in PySide6.
"""

import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFrame, QScrollArea, QAbstractItemView, QTabWidget, QDialog
)

from database.database import (
    add_class,
    get_all_classes,
    update_class,
    delete_class,
    search_classes
)
from ui.class_subjects import ClassSubjectsWindow


class ClassesWindow(QWidget):
    def __init__(self, parent=None, container=None):
        super().__init__(container if container else parent)
        self.parent_window = parent
        self.embedded = container is not None
        self.selected_id = None

        if not self.embedded:
            self.setWindowTitle("Classes & Semesters - Smart Academic Timetable Management System")
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
        lbl_title = QLabel("Classes & Semesters")
        lbl_title.setStyleSheet("font-size: 22px; font-weight: bold;")
        lbl_sub = QLabel("Create and manage student batches, class sections, and course semesters")
        lbl_sub.setProperty("secondary", True)
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        btn_assign_subjects = QPushButton("Assign Class Subjects")
        btn_assign_subjects.setProperty("btnStyle", "secondary")
        btn_assign_subjects.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_assign_subjects.clicked.connect(self.open_class_subjects_modal)
        header_layout.addWidget(btn_assign_subjects)

        main_layout.addWidget(header_card)

        # =====================================================
        # FORM / GENERATOR CARD (TABS)
        # =====================================================
        tab_card = QFrame()
        tab_card.setObjectName("Card")
        tab_card_layout = QVBoxLayout(tab_card)
        tab_card_layout.setContentsMargins(20, 15, 20, 20)

        self.tabs = QTabWidget()

        # Tab 1: Single Class Form
        tab_single = QWidget()
        single_layout = QVBoxLayout(tab_single)
        single_layout.setContentsMargins(15, 15, 15, 10)
        single_layout.setSpacing(14)

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)

        # Row 0: Class Name, Department, Semester, Section
        lbl_cname = QLabel("Class Name *")
        lbl_cname.setStyleSheet("font-weight: 600;")
        self.class_name_entry = QLineEdit()
        self.class_name_entry.setPlaceholderText("e.g. BCA 1st Year - A")
        grid.addWidget(lbl_cname, 0, 0)
        grid.addWidget(self.class_name_entry, 1, 0)

        lbl_dept = QLabel("Department *")
        lbl_dept.setStyleSheet("font-weight: 600;")
        self.dept_entry = QLineEdit()
        self.dept_entry.setPlaceholderText("e.g. BCA")
        grid.addWidget(lbl_dept, 0, 1)
        grid.addWidget(self.dept_entry, 1, 1)

        lbl_sem = QLabel("Semester *")
        lbl_sem.setStyleSheet("font-weight: 600;")
        self.sem_combo = QComboBox()
        self.sem_combo.addItems([str(i) for i in range(1, 9)])
        grid.addWidget(lbl_sem, 0, 2)
        grid.addWidget(self.sem_combo, 1, 2)

        lbl_sec = QLabel("Section")
        lbl_sec.setStyleSheet("font-weight: 600;")
        self.sec_combo = QComboBox()
        self.sec_combo.addItems(["A", "B", "C", "D", "None"])
        grid.addWidget(lbl_sec, 0, 3)
        grid.addWidget(self.sec_combo, 1, 3)

        # Row 1: Academic Year, Total Students
        lbl_ayear = QLabel("Academic Year / Batch")
        lbl_ayear.setStyleSheet("font-weight: 600;")
        self.academic_year_entry = QLineEdit("2024-2025")
        self.academic_year_entry.setPlaceholderText("2024-2025")
        grid.addWidget(lbl_ayear, 2, 0)
        grid.addWidget(self.academic_year_entry, 3, 0)

        lbl_students = QLabel("Total Students")
        lbl_students.setStyleSheet("font-weight: 600;")
        self.students_entry = QLineEdit("50")
        self.students_entry.setPlaceholderText("50")
        grid.addWidget(lbl_students, 2, 1)
        grid.addWidget(self.students_entry, 3, 1)

        single_layout.addLayout(grid)

        # Single Class Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_add = QPushButton("Add Class")
        self.btn_add.setProperty("btnStyle", "success")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.add_class_record)
        btn_layout.addWidget(self.btn_add)

        self.btn_update = QPushButton("Update Selected")
        self.btn_update.setProperty("btnStyle", "secondary")
        self.btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_update.clicked.connect(self.update_class_record)
        btn_layout.addWidget(self.btn_update)

        self.btn_delete = QPushButton("Delete Selected")
        self.btn_delete.setProperty("btnStyle", "danger")
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_class_record)
        btn_layout.addWidget(self.btn_delete)

        self.btn_clear = QPushButton("Clear Form")
        self.btn_clear.setProperty("btnStyle", "ghost")
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.clicked.connect(self.clear_form)
        btn_layout.addWidget(self.btn_clear)

        btn_layout.addStretch()
        single_layout.addLayout(btn_layout)

        self.tabs.addTab(tab_single, "Add / Edit Single Class")

        # Tab 2: Auto Course Duration Generator
        tab_auto = QWidget()
        auto_layout = QVBoxLayout(tab_auto)
        auto_layout.setContentsMargins(15, 15, 15, 10)
        auto_layout.setSpacing(14)

        auto_info = QLabel("Generate all semester classes for an entire degree program automatically.")
        auto_info.setProperty("secondary", True)
        auto_layout.addWidget(auto_info)

        auto_grid = QGridLayout()
        auto_grid.setSpacing(12)
        auto_grid.setColumnStretch(0, 1)
        auto_grid.setColumnStretch(1, 1)
        auto_grid.setColumnStretch(2, 1)
        auto_grid.setColumnStretch(3, 1)

        lbl_gdept = QLabel("Degree / Course Name *")
        lbl_gdept.setStyleSheet("font-weight: 600;")
        self.gen_course_entry = QLineEdit()
        self.gen_course_entry.setPlaceholderText("e.g. BCA or B.Tech CSE")
        auto_grid.addWidget(lbl_gdept, 0, 0)
        auto_grid.addWidget(self.gen_course_entry, 1, 0)

        lbl_gdur = QLabel("Course Duration *")
        lbl_gdur.setStyleSheet("font-weight: 600;")
        self.gen_duration_combo = QComboBox()
        self.gen_duration_combo.addItems([
            "3 Years (6 Semesters)", "4 Years (8 Semesters)", "2 Years (4 Semesters)", "5 Years (10 Semesters)", "1 Year (2 Semesters)"
        ])
        auto_grid.addWidget(lbl_gdur, 0, 1)
        auto_grid.addWidget(self.gen_duration_combo, 1, 1)

        lbl_gsec = QLabel("Sections per Semester")
        lbl_gsec.setStyleSheet("font-weight: 600;")
        self.gen_sections_combo = QComboBox()
        self.gen_sections_combo.addItems(["1 Section (A)", "2 Sections (A, B)", "3 Sections (A, B, C)"])
        auto_grid.addWidget(lbl_gsec, 0, 2)
        auto_grid.addWidget(self.gen_sections_combo, 1, 2)

        lbl_gyear = QLabel("Batch Academic Year")
        lbl_gyear.setStyleSheet("font-weight: 600;")
        self.gen_year_entry = QLineEdit("2024-2025")
        self.gen_year_entry.setPlaceholderText("2024-2025")
        auto_grid.addWidget(lbl_gyear, 0, 3)
        auto_grid.addWidget(self.gen_year_entry, 1, 3)

        auto_layout.addLayout(auto_grid)

        btn_auto_gen = QPushButton("Generate All Course Classes")
        btn_auto_gen.setProperty("btnStyle", "primary")
        btn_auto_gen.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_auto_gen.clicked.connect(self.auto_generate_course_classes)
        auto_layout.addWidget(btn_auto_gen, 0, Qt.AlignmentFlag.AlignLeft)

        self.tabs.addTab(tab_auto, "Bulk Course Generator")

        tab_card_layout.addWidget(self.tabs)
        main_layout.addWidget(tab_card)

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

        lbl_tbl_title = QLabel("Active Classes & Batches")
        lbl_tbl_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        search_layout.addWidget(lbl_tbl_title)
        search_layout.addStretch()

        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search class name, department, semester...")
        self.search_entry.setFixedWidth(260)
        self.search_entry.textChanged.connect(self.search_records)
        search_layout.addWidget(self.search_entry)

        btn_reset = QPushButton("Reset")
        btn_reset.setProperty("btnStyle", "secondary")
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.clicked.connect(lambda: [self.search_entry.clear(), self.load_classes()])
        search_layout.addWidget(btn_reset)

        table_layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Class Name", "Department", "Semester", "Section", "Academic Year", "Students"
        ])
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

    def load_classes(self, records=None):
        if records is None:
            records = get_all_classes() or []

        self.records_data = records
        self.table.setRowCount(0)

        for row_idx, rec in enumerate(records):
            self.table.insertRow(row_idx)
            for col_idx in range(min(7, len(rec))):
                val = rec[col_idx]
                item = QTableWidgetItem(str(val) if val is not None else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if col_idx in [0, 3, 4, 6] else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_idx, col_idx, item)

    def on_table_select(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        if row < len(self.records_data):
            rec = self.records_data[row]
            self.selected_id = rec[0]
            self.class_name_entry.setText(str(rec[1] or ""))
            self.dept_entry.setText(str(rec[2] or ""))
            self.sem_combo.setCurrentText(str(rec[3] or "1"))
            self.sec_combo.setCurrentText(str(rec[4] or "A"))
            self.academic_year_entry.setText(str(rec[5] or "2024-2025"))
            self.students_entry.setText(str(rec[6] or "50"))
            self.tabs.setCurrentIndex(0)

    def clear_form(self):
        self.selected_id = None
        self.class_name_entry.clear()
        self.dept_entry.clear()
        self.sem_combo.setCurrentIndex(0)
        self.sec_combo.setCurrentIndex(0)
        self.academic_year_entry.setText("2024-2025")
        self.students_entry.setText("50")
        self.table.clearSelection()

    def validate_inputs(self):
        cname = self.class_name_entry.text().strip()
        dept = self.dept_entry.text().strip()
        students_str = self.students_entry.text().strip()

        if not cname:
            QMessageBox.warning(self, "Validation Error", "Class Name is required.")
            self.class_name_entry.setFocus()
            return False

        if not dept:
            QMessageBox.warning(self, "Validation Error", "Department is required.")
            self.dept_entry.setFocus()
            return False

        try:
            st = int(students_str)
            if st < 1 or st > 1000:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Total Students must be an integer between 1 and 1000.")
            self.students_entry.setFocus()
            return False

        return True

    def add_class_record(self):
        if not self.validate_inputs():
            return

        cname = self.class_name_entry.text().strip()
        dept = self.dept_entry.text().strip()
        sem = int(self.sem_combo.currentText())
        sec = self.sec_combo.currentText()
        if sec == "None":
            sec = ""
        ayear = self.academic_year_entry.text().strip() or "2024-2025"
        students = int(self.students_entry.text().strip())

        success, msg = add_class(
            class_name=cname,
            department=dept,
            semester=sem,
            section=sec,
            academic_year=ayear,
            total_students=students
        )

        if success:
            QMessageBox.information(self, "Success", "Class created successfully!")
            self.clear_form()
            self.load_classes()
        else:
            QMessageBox.critical(self, "Error", f"Failed to add class:\n{msg}")

    def update_class_record(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Update", "Please select a class from the table to update.")
            return

        if not self.validate_inputs():
            return

        cname = self.class_name_entry.text().strip()
        dept = self.dept_entry.text().strip()
        sem = int(self.sem_combo.currentText())
        sec = self.sec_combo.currentText()
        if sec == "None":
            sec = ""
        ayear = self.academic_year_entry.text().strip() or "2024-2025"
        students = int(self.students_entry.text().strip())

        success, msg = update_class(
            class_db_id=self.selected_id,
            class_name=cname,
            department=dept,
            semester=sem,
            section=sec,
            academic_year=ayear,
            total_students=students
        )

        if success:
            QMessageBox.information(self, "Success", "Class updated successfully!")
            self.clear_form()
            self.load_classes()
        else:
            QMessageBox.critical(self, "Error", f"Failed to update class:\n{msg}")

    def delete_class_record(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Delete", "Please select a class from the table to delete.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{self.class_name_entry.text().strip()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            success, msg = delete_class(self.selected_id)
            if success:
                QMessageBox.information(self, "Deleted", "Class deleted successfully.")
                self.clear_form()
                self.load_classes()
            else:
                QMessageBox.critical(self, "Error", f"Failed to delete class:\n{msg}")

    def auto_generate_course_classes(self):
        course = self.gen_course_entry.text().strip()
        if not course:
            QMessageBox.warning(self, "Course Generator", "Please enter a Course / Degree name.")
            self.gen_course_entry.setFocus()
            return

        dur_text = self.gen_duration_combo.currentText()
        num_sems = 6
        if "8 Semesters" in dur_text:
            num_sems = 8
        elif "4 Semesters" in dur_text:
            num_sems = 4
        elif "10 Semesters" in dur_text:
            num_sems = 10
        elif "2 Semesters" in dur_text:
            num_sems = 2

        sec_text = self.gen_sections_combo.currentText()
        sections = ["A"]
        if "2 Sections" in sec_text:
            sections = ["A", "B"]
        elif "3 Sections" in sec_text:
            sections = ["A", "B", "C"]

        year = self.gen_year_entry.text().strip() or "2024-2025"

        created_count = 0
        for sem in range(1, num_sems + 1):
            for sec in sections:
                class_name = f"{course} - Sem {sem} ({sec})"
                success, _ = add_class(
                    class_name=class_name,
                    department=course,
                    semester=sem,
                    section=sec,
                    academic_year=year,
                    total_students=50
                )
                if success:
                    created_count += 1

        QMessageBox.information(
            self,
            "Generator Completed",
            f"Successfully generated {created_count} class batches for {course}!"
        )
        self.load_classes()
        self.tabs.setCurrentIndex(0)

    def open_class_subjects_modal(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Class - Subject Assignment")
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


if __name__ == "__main__":
    from database.database import create_tables
    from ui.theme import apply_theme

    create_tables()
    app = QApplication.instance() or QApplication(sys.argv)
    apply_theme()
    win = ClassesWindow()
    win.show()
    sys.exit(app.exec())
