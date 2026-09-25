"""
Class - Subject Assignment Window & Embedded Widget in PySide6.
"""

import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFrame, QScrollArea, QAbstractItemView
)

from database.database import (
    get_all_classes,
    get_all_subjects,
    get_all_faculty,
    assign_subject_to_class,
    get_all_class_subjects,
    get_class_subjects_by_class,
    delete_class_subject
)


class ClassSubjectsWindow(QWidget):
    def __init__(self, parent=None, preselected_class_id=None, container=None):
        super().__init__(container if container else parent)
        self.parent_window = parent
        self.embedded = container is not None
        self.preselected_class_id = preselected_class_id
        self.selected_mapping_id = None

        self.classes_data = []
        self.subjects_data = []
        self.faculty_data = []

        if not self.embedded:
            self.setWindowTitle("Class - Subject Assignment - Smart Academic Timetable Management System")
            self.resize(1150, 680)
            self.setMinimumSize(1000, 600)

        self.setup_ui()
        self.load_dropdowns()
        self.load_assigned_subjects()

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
        lbl_title = QLabel("Class - Subject Assignment")
        lbl_title.setStyleSheet("font-size: 22px; font-weight: bold;")
        lbl_sub = QLabel("Map curriculum subjects and assigned faculty to specific academic classes")
        lbl_sub.setProperty("secondary", True)
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        main_layout.addWidget(header_card)

        # =====================================================
        # ASSIGNMENT FORM CARD
        # =====================================================
        form_card = QFrame()
        form_card.setObjectName("Card")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(25, 20, 25, 25)
        form_layout.setSpacing(15)

        form_title = QLabel("Assign Subject to Class")
        form_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        form_layout.addWidget(form_title)

        grid = QGridLayout()
        grid.setSpacing(14)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)

        # Row 0: Target Class, Subject, Faculty, Hours/Week
        lbl_cls = QLabel("Select Academic Class *")
        lbl_cls.setStyleSheet("font-weight: 600;")
        self.class_combo = QComboBox()
        self.class_combo.currentIndexChanged.connect(self.on_class_change)
        grid.addWidget(lbl_cls, 0, 0)
        grid.addWidget(self.class_combo, 1, 0)

        lbl_sub = QLabel("Select Subject *")
        lbl_sub.setStyleSheet("font-weight: 600;")
        self.subject_combo = QComboBox()
        self.subject_combo.currentIndexChanged.connect(self.on_subject_change)
        grid.addWidget(lbl_sub, 0, 1)
        grid.addWidget(self.subject_combo, 1, 1)

        lbl_fac = QLabel("Assigned Faculty")
        lbl_fac.setStyleSheet("font-weight: 600;")
        self.faculty_combo = QComboBox()
        grid.addWidget(lbl_fac, 0, 2)
        grid.addWidget(self.faculty_combo, 1, 2)

        lbl_hrs = QLabel("Hours / Week *")
        lbl_hrs.setStyleSheet("font-weight: 600;")
        self.hours_entry = QLineEdit("4")
        self.hours_entry.setPlaceholderText("4")
        grid.addWidget(lbl_hrs, 0, 3)
        grid.addWidget(self.hours_entry, 1, 3)

        form_layout.addLayout(grid)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_assign = QPushButton("Assign Subject to Class")
        self.btn_assign.setProperty("btnStyle", "success")
        self.btn_assign.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_assign.clicked.connect(self.assign_subject)
        btn_layout.addWidget(self.btn_assign)

        self.btn_delete = QPushButton("Delete Assignment")
        self.btn_delete.setProperty("btnStyle", "danger")
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_assignment)
        btn_layout.addWidget(self.btn_delete)

        btn_layout.addStretch()
        form_layout.addLayout(btn_layout)

        main_layout.addWidget(form_card)

        # =====================================================
        # ASSIGNED SUBJECTS TABLE CARD
        # =====================================================
        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(25, 20, 25, 25)
        table_layout.setSpacing(15)

        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        lbl_tbl = QLabel("Assigned Class Subjects")
        lbl_tbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        filter_layout.addWidget(lbl_tbl)
        filter_layout.addStretch()

        filter_layout.addWidget(QLabel("Filter by Class:"))
        self.filter_class_combo = QComboBox()
        self.filter_class_combo.setMinimumWidth(220)
        self.filter_class_combo.currentIndexChanged.connect(self.filter_table_by_class)
        filter_layout.addWidget(self.filter_class_combo)

        btn_show_all = QPushButton("Show All")
        btn_show_all.setProperty("btnStyle", "secondary")
        btn_show_all.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_show_all.clicked.connect(lambda: self.filter_class_combo.setCurrentIndex(0))
        filter_layout.addWidget(btn_show_all)

        table_layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Class Name", "Subject Code", "Subject Name", "Faculty", "Weekly Hours", "Type"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
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
        self.classes_data = get_all_classes() or []
        self.class_combo.clear()
        self.filter_class_combo.clear()
        self.filter_class_combo.addItem("All Classes", None)

        selected_idx = 0
        for idx, c in enumerate(self.classes_data):
            cid = c[0]
            cname = c[1]
            dept = c[2] if len(c) > 2 else ""
            sem = c[3] if len(c) > 3 else ""
            display = f"{cname} (Sem {sem}, {dept})"
            self.class_combo.addItem(display, cid)
            self.filter_class_combo.addItem(display, cid)
            if self.preselected_class_id and cid == self.preselected_class_id:
                selected_idx = idx

        if self.classes_data:
            self.class_combo.setCurrentIndex(selected_idx)

        self.subjects_data = get_all_subjects() or []
        self.subject_combo.clear()
        for s in self.subjects_data:
            sid = s[0]
            code = s[1]
            sname = s[2]
            hrs = s[6] if len(s) > 6 else 4
            self.subject_combo.addItem(f"{code} - {sname}", (sid, hrs))

        self.faculty_data = get_all_faculty() or []
        self.faculty_combo.clear()
        self.faculty_combo.addItem("None / Auto-Assign", None)
        for f in self.faculty_data:
            fid = f[0]
            fname = f[2]
            dept = f[3] if len(f) > 3 else ""
            self.faculty_combo.addItem(f"{fname} ({dept})", fid)

    def on_class_change(self):
        pass

    def on_subject_change(self):
        data = self.subject_combo.currentData()
        if data and len(data) > 1:
            self.hours_entry.setText(str(data[1] or 4))

    def load_assigned_subjects(self, records=None):
        if records is None:
            records = get_all_class_subjects() or []

        self.records_data = records
        self.table.setRowCount(0)

        for row_idx, rec in enumerate(records):
            self.table.insertRow(row_idx)
            mid = rec[0] if len(rec) > 0 else ""
            cname = rec[4] if len(rec) > 4 else (rec[1] if len(rec) > 1 else "")
            scode = rec[5] if len(rec) > 5 else ""
            sname = rec[6] if len(rec) > 6 else ""
            fname = rec[7] if len(rec) > 7 and rec[7] else "Unassigned"
            hrs = rec[3] if len(rec) > 3 else ""
            is_lab = "Lab" if (len(rec) > 8 and rec[8] == 1) else "Theory"

            row_items = [str(mid), str(cname), str(scode), str(sname), str(fname), str(hrs), is_lab]
            for col_idx, text in enumerate(row_items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if col_idx in [0, 2, 5, 6] else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_idx, col_idx, item)

    def filter_table_by_class(self):
        selected_cid = self.filter_class_combo.currentData()
        if selected_cid is None:
            self.load_assigned_subjects()
        else:
            records = get_class_subjects_by_class(selected_cid) or []
            self.load_assigned_subjects(records)

    def on_table_select(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.selected_mapping_id = None
            return

        row = selected_items[0].row()
        if row < len(self.records_data):
            self.selected_mapping_id = self.records_data[row][0]

    def assign_subject(self):
        if self.class_combo.currentIndex() < 0 or not self.classes_data:
            QMessageBox.warning(self, "Assignment", "Please select a valid class.")
            return

        if self.subject_combo.currentIndex() < 0 or not self.subjects_data:
            QMessageBox.warning(self, "Assignment", "Please select a valid subject.")
            return

        class_id = self.class_combo.currentData()
        subject_data = self.subject_combo.currentData()
        subject_id = subject_data[0] if isinstance(subject_data, tuple) else subject_data

        faculty_id = self.faculty_combo.currentData()

        try:
            hrs = int(self.hours_entry.text().strip())
            if hrs < 1 or hrs > 30:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Hours/Week must be between 1 and 30.")
            return

        success, msg = assign_subject_to_class(
            class_id=class_id,
            subject_id=subject_id,
            faculty_id=faculty_id,
            hours_per_week=hrs
        )

        if success:
            QMessageBox.information(self, "Success", "Subject successfully assigned to class!")
            self.load_assigned_subjects()
        else:
            QMessageBox.critical(self, "Error", f"Failed to assign subject:\n{msg}")

    def delete_assignment(self):
        if not self.selected_mapping_id:
            QMessageBox.warning(self, "Delete", "Please select an assigned subject row to remove.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Removal",
            "Are you sure you want to remove this subject assignment?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            success, msg = delete_class_subject(self.selected_mapping_id)
            if success:
                QMessageBox.information(self, "Deleted", "Subject assignment removed.")
                self.selected_mapping_id = None
                self.load_assigned_subjects()
            else:
                QMessageBox.critical(self, "Error", f"Failed to remove assignment:\n{msg}")


if __name__ == "__main__":
    from database.database import create_tables
    from ui.theme import apply_theme

    create_tables()
    app = QApplication.instance() or QApplication(sys.argv)
    apply_theme()
    win = ClassSubjectsWindow()
    win.show()
    sys.exit(app.exec())
