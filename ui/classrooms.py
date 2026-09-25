"""
Classroom Management Window & Embedded Widget in PySide6.
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
    add_classroom,
    get_all_classrooms,
    update_classroom,
    delete_classroom,
    search_classrooms
)


class ClassroomsWindow(QWidget):
    def __init__(self, parent=None, container=None):
        super().__init__(container if container else parent)
        self.parent_window = parent
        self.embedded = container is not None
        self.selected_id = None

        if not self.embedded:
            self.setWindowTitle("Classroom Management - Smart Academic Timetable Management System")
            self.resize(1150, 720)
            self.setMinimumSize(1000, 650)

        self.setup_ui()
        self.load_classrooms()

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
        lbl_title = QLabel("Classroom Management")
        lbl_title.setStyleSheet("font-size: 22px; font-weight: bold;")
        lbl_sub = QLabel("Add and manage lecture halls, laboratories, smart classrooms, and seating capacities")
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

        form_title = QLabel("Classroom Details")
        form_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        form_layout.addWidget(form_title)

        grid = QGridLayout()
        grid.setSpacing(14)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)

        # Row 0: Room Number, Room Name, Building
        lbl_rnum = QLabel("Room Number / Code *")
        lbl_rnum.setStyleSheet("font-weight: 600;")
        self.room_number_entry = QLineEdit()
        self.room_number_entry.setPlaceholderText("e.g. LH-101 or LAB-02")
        grid.addWidget(lbl_rnum, 0, 0)
        grid.addWidget(self.room_number_entry, 1, 0)

        lbl_rname = QLabel("Room Name")
        lbl_rname.setStyleSheet("font-weight: 600;")
        self.room_name_entry = QLineEdit()
        self.room_name_entry.setPlaceholderText("e.g. Turing Hall / AI Lab")
        grid.addWidget(lbl_rname, 0, 1)
        grid.addWidget(self.room_name_entry, 1, 1)

        lbl_bld = QLabel("Building / Floor")
        lbl_bld.setStyleSheet("font-weight: 600;")
        self.building_entry = QLineEdit()
        self.building_entry.setPlaceholderText("e.g. Main Block, 1st Floor")
        grid.addWidget(lbl_bld, 0, 2)
        grid.addWidget(self.building_entry, 1, 2)

        # Row 1: Capacity, Room Type
        lbl_cap = QLabel("Seating Capacity *")
        lbl_cap.setStyleSheet("font-weight: 600;")
        self.capacity_entry = QLineEdit("60")
        self.capacity_entry.setPlaceholderText("60")
        grid.addWidget(lbl_cap, 2, 0)
        grid.addWidget(self.capacity_entry, 3, 0)

        lbl_rtype = QLabel("Room Type *")
        lbl_rtype.setStyleSheet("font-weight: 600;")
        self.room_type_combo = QComboBox()
        self.room_type_combo.addItems([
            "Lecture Hall", "Computer Lab", "Science Lab", "Seminar Room", "Smart Classroom", "Workshop"
        ])
        grid.addWidget(lbl_rtype, 2, 1)
        grid.addWidget(self.room_type_combo, 3, 1)

        form_layout.addLayout(grid)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_add = QPushButton("Add Classroom")
        self.btn_add.setProperty("btnStyle", "success")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.add_classroom_record)
        btn_layout.addWidget(self.btn_add)

        self.btn_update = QPushButton("Update Selected")
        self.btn_update.setProperty("btnStyle", "secondary")
        self.btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_update.clicked.connect(self.update_classroom_record)
        btn_layout.addWidget(self.btn_update)

        self.btn_delete = QPushButton("Delete Selected")
        self.btn_delete.setProperty("btnStyle", "danger")
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_classroom_record)
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

        lbl_tbl_title = QLabel("Available Classrooms & Facilities")
        lbl_tbl_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        search_layout.addWidget(lbl_tbl_title)
        search_layout.addStretch()

        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search room number, building, type...")
        self.search_entry.setFixedWidth(260)
        self.search_entry.textChanged.connect(self.search_records)
        search_layout.addWidget(self.search_entry)

        btn_reset = QPushButton("Reset")
        btn_reset.setProperty("btnStyle", "secondary")
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.clicked.connect(lambda: [self.search_entry.clear(), self.load_classrooms()])
        search_layout.addWidget(btn_reset)

        table_layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Room Number", "Room Name", "Building / Floor", "Capacity", "Room Type"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setMinimumHeight(300)
        self.table.itemSelectionChanged.connect(self.on_table_select)

        table_layout.addWidget(self.table)
        main_layout.addWidget(table_card)
        main_layout.addStretch()

    def load_classrooms(self, records=None):
        if records is None:
            records = get_all_classrooms() or []

        self.records_data = records
        self.table.setRowCount(0)

        for row_idx, rec in enumerate(records):
            self.table.insertRow(row_idx)
            for col_idx in range(min(6, len(rec))):
                val = rec[col_idx]
                item = QTableWidgetItem(str(val) if val is not None else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if col_idx in [0, 1, 4] else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_idx, col_idx, item)

    def on_table_select(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        if row < len(self.records_data):
            rec = self.records_data[row]
            self.selected_id = rec[0]
            self.room_number_entry.setText(str(rec[1] or ""))
            self.room_name_entry.setText(str(rec[2] or ""))
            self.building_entry.setText(str(rec[3] or ""))
            self.capacity_entry.setText(str(rec[4] or "60"))
            if len(rec) > 5 and rec[5]:
                self.room_type_combo.setCurrentText(str(rec[5]))

    def clear_form(self):
        self.selected_id = None
        self.room_number_entry.clear()
        self.room_name_entry.clear()
        self.building_entry.clear()
        self.capacity_entry.setText("60")
        self.room_type_combo.setCurrentIndex(0)
        self.table.clearSelection()

    def validate_inputs(self):
        rnum = self.room_number_entry.text().strip()
        cap_str = self.capacity_entry.text().strip()

        if not rnum:
            QMessageBox.warning(self, "Validation Error", "Room Number is required.")
            self.room_number_entry.setFocus()
            return False

        try:
            cap = int(cap_str)
            if cap < 1 or cap > 1000:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Capacity must be an integer between 1 and 1000.")
            self.capacity_entry.setFocus()
            return False

        return True

    def add_classroom_record(self):
        if not self.validate_inputs():
            return

        rnum = self.room_number_entry.text().strip()
        rname = self.room_name_entry.text().strip() or None
        bld = self.building_entry.text().strip() or None
        cap = int(self.capacity_entry.text().strip())
        rtype = self.room_type_combo.currentText()

        success, msg = add_classroom(
            room_number=rnum,
            room_name=rname,
            building=bld,
            capacity=cap,
            room_type=rtype
        )

        if success:
            QMessageBox.information(self, "Success", "Classroom added successfully!")
            self.clear_form()
            self.load_classrooms()
        else:
            QMessageBox.critical(self, "Error", f"Failed to add classroom:\n{msg}")

    def update_classroom_record(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Update", "Please select a classroom from the table to update.")
            return

        if not self.validate_inputs():
            return

        rnum = self.room_number_entry.text().strip()
        rname = self.room_name_entry.text().strip() or None
        bld = self.building_entry.text().strip() or None
        cap = int(self.capacity_entry.text().strip())
        rtype = self.room_type_combo.currentText()

        success, msg = update_classroom(
            classroom_db_id=self.selected_id,
            room_number=rnum,
            room_name=rname,
            building=bld,
            capacity=cap,
            room_type=rtype
        )

        if success:
            QMessageBox.information(self, "Success", "Classroom updated successfully!")
            self.clear_form()
            self.load_classrooms()
        else:
            QMessageBox.critical(self, "Error", f"Failed to update classroom:\n{msg}")

    def delete_classroom_record(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Delete", "Please select a classroom from the table to delete.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete classroom '{self.room_number_entry.text().strip()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            success, msg = delete_classroom(self.selected_id)
            if success:
                QMessageBox.information(self, "Deleted", "Classroom deleted successfully.")
                self.clear_form()
                self.load_classrooms()
            else:
                QMessageBox.critical(self, "Error", f"Failed to delete classroom:\n{msg}")

    def search_records(self, text):
        query = text.strip()
        if not query:
            self.load_classrooms()
        else:
            records = search_classrooms(query) or []
            self.load_classrooms(records)


if __name__ == "__main__":
    from database.database import create_tables
    from ui.theme import apply_theme

    create_tables()
    app = QApplication.instance() or QApplication(sys.argv)
    apply_theme()
    win = ClassroomsWindow()
    win.show()
    sys.exit(app.exec())
