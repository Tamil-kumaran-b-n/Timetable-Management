"""
Faculty Workload Management Window & Embedded Widget in PySide6.
"""

import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFrame, QScrollArea, QAbstractItemView, QProgressBar
)

from database.database import (
    get_all_faculty,
    get_all_classes,
    get_all_subjects
)
from database.workload import (
    add_workload,
    get_all_workloads,
    update_workload,
    delete_workload
)


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
            self.setWindowTitle("Faculty Workload Management - Smart Academic Timetable Management System")
            self.resize(1200, 760)
            self.setMinimumSize(1050, 680)

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
        lbl_title = QLabel("Faculty Workload Management")
        lbl_title.setStyleSheet("font-size: 22px; font-weight: bold;")
        lbl_sub = QLabel("Assign multiple classes and subject teaching hours per faculty member")
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

        form_title = QLabel("Workload Assignment Details")
        form_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        form_layout.addWidget(form_title)

        grid = QGridLayout()
        grid.setSpacing(14)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)

        # Row 0: Faculty, Class, Subject, Priority
        lbl_fac = QLabel("Faculty Member *")
        lbl_fac.setStyleSheet("font-weight: 600;")
        self.faculty_combo = QComboBox()
        self.faculty_combo.currentIndexChanged.connect(self.update_faculty_capacity_indicator)
        grid.addWidget(lbl_fac, 0, 0)
        grid.addWidget(self.faculty_combo, 1, 0)

        lbl_cls = QLabel("Academic Class *")
        lbl_cls.setStyleSheet("font-weight: 600;")
        self.class_combo = QComboBox()
        grid.addWidget(lbl_cls, 0, 1)
        grid.addWidget(self.class_combo, 1, 1)

        lbl_sub = QLabel("Subject *")
        lbl_sub.setStyleSheet("font-weight: 600;")
        self.subject_combo = QComboBox()
        self.subject_combo.currentIndexChanged.connect(self.on_subject_change)
        grid.addWidget(lbl_sub, 0, 2)
        grid.addWidget(self.subject_combo, 1, 2)

        lbl_prio = QLabel("Priority / Type")
        lbl_prio.setStyleSheet("font-weight: 600;")
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Normal", "High Priority", "Low Priority", "Guest / Core"])
        grid.addWidget(lbl_prio, 0, 3)
        grid.addWidget(self.priority_combo, 1, 3)

        # Row 1: Periods/Week + Workload status bar
        lbl_periods = QLabel("Periods / Week *")
        lbl_periods.setStyleSheet("font-weight: 600;")
        self.periods_entry = QLineEdit("4")
        self.periods_entry.setPlaceholderText("4")
        grid.addWidget(lbl_periods, 2, 0)
        grid.addWidget(self.periods_entry, 3, 0)

        # Workload status gauge
        load_box = QVBoxLayout()
        load_box.setSpacing(4)
        self.lbl_workload_status = QLabel("Faculty Load: 0 / 18 hrs")
        self.lbl_workload_status.setStyleSheet("font-weight: 600; color: #2563EB;")
        self.workload_progress = QProgressBar()
        self.workload_progress.setRange(0, 24)
        self.workload_progress.setValue(0)
        self.workload_progress.setFixedHeight(16)
        load_box.addWidget(self.lbl_workload_status)
        load_box.addWidget(self.workload_progress)
        grid.addLayout(load_box, 3, 1, 1, 3)

        form_layout.addLayout(grid)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_add = QPushButton("Assign Workload")
        self.btn_add.setProperty("btnStyle", "success")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.add_workload_record)
        btn_layout.addWidget(self.btn_add)

        self.btn_update = QPushButton("Update Selected")
        self.btn_update.setProperty("btnStyle", "secondary")
        self.btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_update.clicked.connect(self.update_workload_record)
        btn_layout.addWidget(self.btn_update)

        self.btn_delete = QPushButton("Delete Selected")
        self.btn_delete.setProperty("btnStyle", "danger")
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_workload_record)
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
        # TABLE CARD
        # =====================================================
        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(25, 20, 25, 25)
        table_layout.setSpacing(15)

        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        lbl_tbl = QLabel("Allocated Faculty Workloads")
        lbl_tbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        filter_layout.addWidget(lbl_tbl)
        filter_layout.addStretch()

        filter_layout.addWidget(QLabel("Filter by Faculty:"))
        self.filter_faculty_combo = QComboBox()
        self.filter_faculty_combo.setMinimumWidth(220)
        self.filter_faculty_combo.currentIndexChanged.connect(self.filter_table_by_faculty)
        filter_layout.addWidget(self.filter_faculty_combo)

        btn_show_all = QPushButton("Show All")
        btn_show_all.setProperty("btnStyle", "secondary")
        btn_show_all.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_show_all.clicked.connect(lambda: self.filter_faculty_combo.setCurrentIndex(0))
        filter_layout.addWidget(btn_show_all)

        table_layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Faculty Name", "Class Name", "Semester", "Subject Code", "Subject Name", "Priority", "Hrs / Wk"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
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

    def load_dropdowns(self):
        self.faculty_records = get_all_faculty() or []
        self.faculty_combo.clear()
        self.filter_faculty_combo.clear()
        self.filter_faculty_combo.addItem("All Faculty Members", None)

        selected_idx = 0
        for idx, f in enumerate(self.faculty_records):
            fid = f[0]
            fname = f[2]
            dept = f[3] if len(f) > 3 else ""
            max_hrs = f[7] if len(f) > 7 else 18
            display = f"{fname} ({dept})"
            self.faculty_combo.addItem(display, (fid, max_hrs))
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
            sem = c[3] if len(c) > 3 else ""
            self.class_combo.addItem(f"{cname} (Sem {sem})", cid)

        self.subject_records = get_all_subjects() or []
        self.subject_combo.clear()
        for s in self.subject_records:
            sid = s[0]
            code = s[1]
            sname = s[2]
            hrs = s[6] if len(s) > 6 else 4
            self.subject_combo.addItem(f"{code} - {sname}", (sid, hrs))

    def on_subject_change(self):
        data = self.subject_combo.currentData()
        if data and len(data) > 1:
            self.periods_entry.setText(str(data[1] or 4))

    def update_faculty_capacity_indicator(self):
        data = self.faculty_combo.currentData()
        if not data:
            return
        fid, max_hrs = data if isinstance(data, tuple) else (data, 18)

        all_wl = get_all_workloads() or []
        current_hrs = 0
        for w in all_wl:
            if len(w) > 1 and w[1] == fid:
                current_hrs += int(w[13] if len(w) > 13 else 0)

        self.workload_progress.setMaximum(max(24, max_hrs))
        self.workload_progress.setValue(current_hrs)

        if current_hrs > max_hrs:
            status_text = f"Faculty Load: {current_hrs} / {max_hrs} hrs (Overloaded)"
            self.lbl_workload_status.setStyleSheet("font-weight: 600; color: #EF4444;")
        elif current_hrs == max_hrs:
            status_text = f"Faculty Load: {current_hrs} / {max_hrs} hrs (Full Capacity)"
            self.lbl_workload_status.setStyleSheet("font-weight: 600; color: #10B981;")
        else:
            status_text = f"Faculty Load: {current_hrs} / {max_hrs} hrs (Available: {max_hrs - current_hrs} hrs)"
            self.lbl_workload_status.setStyleSheet("font-weight: 600; color: #2563EB;")

        self.lbl_workload_status.setText(status_text)

    def load_workloads(self, records=None):
        if records is None:
            records = get_all_workloads() or []

        self.records_data = records
        self.table.setRowCount(0)

        for row_idx, rec in enumerate(records):
            self.table.insertRow(row_idx)
            wid = rec[0] if len(rec) > 0 else ""
            fname = rec[3] if len(rec) > 3 else ""
            cname = rec[5] if len(rec) > 5 else ""
            sem = f"Sem {rec[7]}" if len(rec) > 7 and rec[7] else "—"
            scode = rec[10] if len(rec) > 10 else ""
            sname = rec[11] if len(rec) > 11 else ""
            prio = rec[12] if len(rec) > 12 else "Normal"
            hrs = rec[13] if len(rec) > 13 else ""

            row_items = [str(wid), str(fname), str(cname), str(sem), str(scode), str(sname), str(prio), str(hrs)]
            for col_idx, text in enumerate(row_items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if col_idx in [0, 3, 4, 6, 7] else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_idx, col_idx, item)

        self.update_faculty_capacity_indicator()

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
            prio = rec[12] if len(rec) > 12 else "Normal"
            hrs = rec[13] if len(rec) > 13 else 4

            for i in range(self.faculty_combo.count()):
                d = self.faculty_combo.itemData(i)
                if d and (d[0] == fid if isinstance(d, tuple) else d == fid):
                    self.faculty_combo.setCurrentIndex(i)
                    break

            for i in range(self.class_combo.count()):
                if self.class_combo.itemData(i) == cid:
                    self.class_combo.setCurrentIndex(i)
                    break

            for i in range(self.subject_combo.count()):
                d = self.subject_combo.itemData(i)
                if d and (d[0] == sid if isinstance(d, tuple) else d == sid):
                    self.subject_combo.setCurrentIndex(i)
                    break

            self.priority_combo.setCurrentText(str(prio))
            self.periods_entry.setText(str(hrs))

    def clear_form(self):
        self.selected_workload_id = None
        self.periods_entry.setText("4")
        self.priority_combo.setCurrentIndex(0)
        self.table.clearSelection()
        self.update_faculty_capacity_indicator()

    def add_workload_record(self):
        fac_data = self.faculty_combo.currentData()
        if not fac_data:
            QMessageBox.warning(self, "Validation Error", "Please select a faculty member.")
            return
        faculty_id = fac_data[0] if isinstance(fac_data, tuple) else fac_data

        class_id = self.class_combo.currentData()
        if not class_id:
            QMessageBox.warning(self, "Validation Error", "Please select an academic class.")
            return

        sub_data = self.subject_combo.currentData()
        if not sub_data:
            QMessageBox.warning(self, "Validation Error", "Please select a subject.")
            return
        subject_id = sub_data[0] if isinstance(sub_data, tuple) else sub_data

        try:
            hrs = int(self.periods_entry.text().strip())
            if hrs < 1 or hrs > 30:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Periods/Week must be an integer between 1 and 30.")
            return

        prio = self.priority_combo.currentText()

        workload_id = add_workload(
            faculty_id=faculty_id,
            class_id=class_id,
            subject_id=subject_id,
            priority=prio,
            periods_per_week=hrs
        )

        if workload_id is not None:
            QMessageBox.information(self, "Success", "Faculty workload assigned successfully!")
            self.clear_form()
            self.load_workloads()
        else:
            QMessageBox.critical(self, "Error", "Failed to assign workload. This Faculty-Class-Subject combination already exists.")

    def update_workload_record(self):
        if not self.selected_workload_id:
            QMessageBox.warning(self, "Update", "Please select a workload record from the table to update.")
            return

        fac_data = self.faculty_combo.currentData()
        faculty_id = fac_data[0] if isinstance(fac_data, tuple) else fac_data
        class_id = self.class_combo.currentData()
        sub_data = self.subject_combo.currentData()
        subject_id = sub_data[0] if isinstance(sub_data, tuple) else sub_data

        try:
            hrs = int(self.periods_entry.text().strip())
            if hrs < 1 or hrs > 30:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Periods/Week must be an integer between 1 and 30.")
            return

        prio = self.priority_combo.currentText()

        success = update_workload(
            workload_id=self.selected_workload_id,
            faculty_id=faculty_id,
            class_id=class_id,
            subject_id=subject_id,
            priority=prio,
            periods_per_week=hrs
        )

        if success:
            QMessageBox.information(self, "Success", "Workload updated successfully!")
            self.clear_form()
            self.load_workloads()
        else:
            QMessageBox.critical(self, "Error", "Failed to update workload.")

    def delete_workload_record(self):
        if not self.selected_workload_id:
            QMessageBox.warning(self, "Delete", "Please select a workload record from the table to delete.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to remove this faculty workload assignment?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            success = delete_workload(self.selected_workload_id)
            if success:
                QMessageBox.information(self, "Deleted", "Workload deleted successfully.")
                self.clear_form()
                self.load_workloads()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete workload.")


if __name__ == "__main__":
    from database.database import create_tables
    from ui.theme import apply_theme

    create_tables()
    app = QApplication.instance() or QApplication(sys.argv)
    apply_theme()
    win = AssignmentsWindow()
    win.show()
    sys.exit(app.exec())
