import csv
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame, QScrollArea, QFileDialog, QRadioButton, QButtonGroup, QDialog
from database.database import get_all_faculty, get_all_classes
from database.generator import get_timetable_by_class, get_timetable_by_faculty, get_all_timetable, clear_timetable
from ui.theme import get_active_palette

class ViewTimetableWindow(QWidget):

    def __init__(self, parent=None, container=None, faculty_user=None):
        super().__init__(container if container else parent)
        self.parent_window = parent
        self.embedded = container is not None
        self.faculty_user = faculty_user
        self.current_mode = 'class' if not faculty_user else 'faculty'
        self.current_id = None
        self.current_timetable_data = []
        self.faculty_records = []
        self.class_records = []
        if not self.embedded:
            self.setWindowTitle('View Timetable - Smart Academic Timetable Management System')
            self.resize(1280, 800)
            self.setMinimumSize(1100, 700)
        self.setup_ui()
        self.load_dropdowns()
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
        scroll_content.setMinimumWidth(850)
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
        title_str = 'My Timetable' if self.faculty_user else 'Timetable'
        lbl_title = QLabel(title_str)
        lbl_title.setStyleSheet('font-size: 22px; font-weight: bold;')
        sub_str = 'View schedule and download PDF' if self.faculty_user else 'View schedules by class or faculty'
        lbl_sub = QLabel(sub_str)
        lbl_sub.setProperty('secondary', True)
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        btn_pdf = QPushButton('Download PDF')
        btn_pdf.setProperty('btnStyle', 'primary')
        btn_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pdf.clicked.connect(self.download_pdf)
        header_layout.addWidget(btn_pdf)
        btn_csv = QPushButton('Export CSV')
        btn_csv.setProperty('btnStyle', 'secondary')
        btn_csv.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_csv.clicked.connect(self.export_csv)
        header_layout.addWidget(btn_csv)
        if not self.faculty_user:
            btn_clear = QPushButton('Clear All')
            btn_clear.setProperty('btnStyle', 'outline-danger')
            btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_clear.clicked.connect(self.clear_all_timetables)
            header_layout.addWidget(btn_clear)
        main_layout.addWidget(header_card)
        filter_card = QFrame()
        filter_card.setObjectName('Card')
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(25, 16, 25, 16)
        filter_layout.setSpacing(20)
        if not self.faculty_user:
            mode_box = QHBoxLayout()
            mode_box.setSpacing(15)
            self.radio_class = QRadioButton('By Class')
            self.radio_class.setChecked(True)
            self.radio_class.toggled.connect(self.on_mode_change)
            self.radio_faculty = QRadioButton('By Faculty')
            self.radio_faculty.toggled.connect(self.on_mode_change)
            self.mode_group = QButtonGroup(self)
            self.mode_group.addButton(self.radio_class)
            self.mode_group.addButton(self.radio_faculty)
            mode_box.addWidget(self.radio_class)
            mode_box.addWidget(self.radio_faculty)
            filter_layout.addLayout(mode_box)
            filter_layout.addSpacing(15)
        self.lbl_target = QLabel('Class:')
        self.lbl_target.setStyleSheet('font-weight: 600;')
        filter_layout.addWidget(self.lbl_target)
        self.target_combo = QComboBox()
        self.target_combo.setMinimumWidth(320)
        self.target_combo.currentIndexChanged.connect(self.load_timetable_grid)
        filter_layout.addWidget(self.target_combo)
        btn_refresh = QPushButton('Refresh')
        btn_refresh.setProperty('btnStyle', 'secondary')
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.clicked.connect(self.load_timetable_grid)
        filter_layout.addWidget(btn_refresh)
        filter_layout.addStretch()
        main_layout.addWidget(filter_card)
        self.grid_card = QFrame()
        self.grid_card.setObjectName('Card')
        self.grid_card_layout = QVBoxLayout(self.grid_card)
        self.grid_card_layout.setContentsMargins(25, 20, 25, 25)
        self.grid_card_layout.setSpacing(15)
        self.lbl_grid_title = QLabel('Schedule')
        self.lbl_grid_title.setStyleSheet('font-size: 18px; font-weight: bold;')
        self.grid_card_layout.addWidget(self.lbl_grid_title)
        self.grid_table = QTableWidget()
        self.grid_table.setRowCount(6)
        self.grid_table.setColumnCount(6)
        self.grid_table.setHorizontalHeaderLabels(['Day Order', 'Period 1', 'Period 2', 'Period 3', 'Period 4', 'Period 5'])
        self.grid_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.grid_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.grid_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.grid_table.verticalHeader().setVisible(False)
        self.grid_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.grid_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.grid_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.grid_table.setMinimumHeight(480)
        self.grid_card_layout.addWidget(self.grid_table)
        main_layout.addWidget(self.grid_card)
        main_layout.addStretch()

    def load_dropdowns(self):
        self.class_records = get_all_classes() or []
        self.faculty_records = get_all_faculty() or []
        self.update_target_combo()

    def on_mode_change(self):
        self.current_mode = 'class' if self.radio_class.isChecked() else 'faculty'
        self.update_target_combo()

    def update_target_combo(self):
        self.target_combo.blockSignals(True)
        self.target_combo.clear()
        if self.faculty_user:
            self.current_mode = 'faculty'
            self.lbl_target.setText('Faculty:')
            fac_user_id = self.faculty_user.get('id')
            fac_id = self.faculty_user.get('faculty_id')
            fac_code = self.faculty_user.get('faculty_code')
            fac_full_name = self.faculty_user.get('full_name') or ''
            fac_username = self.faculty_user.get('username', '')
            matched_fac = None
            for f in self.faculty_records:
                if fac_id is not None and f[0] == fac_id:
                    matched_fac = f
                    break
                if fac_code and str(f[1]).strip().lower() == str(fac_code).strip().lower():
                    matched_fac = f
                    break
                if fac_full_name and str(f[2]).strip().lower() == str(fac_full_name).strip().lower():
                    matched_fac = f
                    break
                if fac_username and (str(f[1]).strip().lower() == str(fac_username).strip().lower() or str(f[2]).strip().lower() == str(fac_username).strip().lower()):
                    matched_fac = f
                    break
            if matched_fac:
                self.target_combo.addItem(f'{matched_fac[2]} ({matched_fac[3]})', matched_fac[0])
            else:
                display_name = fac_full_name or fac_username or 'Faculty'
                self.target_combo.addItem(display_name, fac_id if fac_id is not None else fac_user_id)
        elif self.current_mode == 'class':
            self.lbl_target.setText('Select Class:')
            for c in self.class_records:
                cid = c[0]
                cname = c[1]
                dept = c[2] if len(c) > 2 else ''
                sem = c[3] if len(c) > 3 else ''
                self.target_combo.addItem(f'{cname} • {dept} (Sem {sem})', cid)
        else:
            self.lbl_target.setText('Select Faculty:')
            for f in self.faculty_records:
                fid = f[0]
                fcode = f[1] if len(f) > 1 else ''
                fname = f[2] if len(f) > 2 else ''
                dept = f[3] if len(f) > 3 else ''
                self.target_combo.addItem(f'{fname} ({dept}) • {fcode}', fid)
        self.target_combo.blockSignals(False)
        self.load_timetable_grid()

    def load_timetable_grid(self):
        if self.target_combo.count() == 0:
            self.render_empty_grid('No records available to display.')
            return
        target_id = self.target_combo.currentData()
        self.current_id = target_id
        if not target_id:
            self.render_empty_grid('Please select a valid class or faculty member.')
            return
        if self.current_mode == 'class':
            self.lbl_grid_title.setText(f'Timetable Schedule: {self.target_combo.currentText()}')
            data = get_timetable_by_class(target_id) or []
        else:
            self.lbl_grid_title.setText(f'Faculty Schedule: {self.target_combo.currentText()}')
            data = get_timetable_by_faculty(target_id) or []
        self.current_timetable_data = data
        if not data:
            self.render_empty_grid("No generated timetable slots found for this selection.\nGenerate a timetable from the 'Generate Timetable' menu first.")
            return
        self.render_grid(data)

    def render_empty_grid(self, msg):
        palette = get_active_palette()
        self.grid_table.clearContents()
        self.grid_table.setRowCount(6)
        for day in range(1, 7):
            row_idx = day - 1
            day_item = QTableWidgetItem(f'Day Order {day}')
            day_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            day_item.setForeground(QColor(palette.TEXT_PRIMARY))
            self.grid_table.setItem(row_idx, 0, day_item)
            for p in range(1, 6):
                empty_item = QTableWidgetItem('—')
                empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                empty_item.setForeground(QColor(palette.TEXT_MUTED))
                self.grid_table.setItem(row_idx, p, empty_item)

    def render_grid(self, data):
        palette = get_active_palette()
        self.grid_table.clearContents()
        self.grid_table.setRowCount(6)
        slot_map = {}
        for row in data:
            day_o = row[0]
            period = row[1]
            slot_map[day_o, period] = row
        for day in range(1, 7):
            row_idx = day - 1
            day_item = QTableWidgetItem(f'Day Order {day}')
            day_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            day_item.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
            day_item.setForeground(QColor(palette.TEXT_PRIMARY))
            self.grid_table.setItem(row_idx, 0, day_item)
            for p in range(1, 6):
                col_idx = p
                slot = slot_map.get((day, p))
                if slot:
                    if self.current_mode == 'class':
                        scode = slot[3] if len(slot) > 3 else ''
                        sname = slot[4] if len(slot) > 4 else ''
                        fac_name = slot[5] if len(slot) > 5 else ''
                        cell_text = f'{scode}\n{sname}\nFaculty: {fac_name}'
                    else:
                        cname = slot[3] if len(slot) > 3 else ''
                        scode = slot[4] if len(slot) > 4 else ''
                        sname = slot[5] if len(slot) > 5 else ''
                        sem = slot[6] if len(slot) > 6 and slot[6] else ''
                        sem_str = f' (Sem {sem})' if sem else ''
                        cell_text = f'{scode}\n{sname}\nClass: {cname}{sem_str}'
                    item = QTableWidgetItem(cell_text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setBackground(QColor(palette.BG_TIMETABLE_SLOT))
                    item.setForeground(QColor(palette.TEXT_PRIMARY))
                    self.grid_table.setItem(row_idx, col_idx, item)
                else:
                    item = QTableWidgetItem('FREE PERIOD\n—')
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setBackground(QColor(palette.BG_TIMETABLE_FREE))
                    item.setForeground(QColor(palette.TEXT_MUTED))
                    self.grid_table.setItem(row_idx, col_idx, item)

    def get_download_path(self, ext='pdf'):
        name_clean = re.sub('[\\\\/*?:"<>|]', '', self.target_combo.currentText()).strip().replace(' ', '_')
        default_dir = str(Path.home() / 'Downloads')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return os.path.join(default_dir, f'Timetable_{name_clean}_{timestamp}.{ext}')

    def download_pdf(self):
        if not self.current_timetable_data:
            QMessageBox.warning(self, 'Export PDF', 'No timetable schedule available to export.')
            return
        save_path, _ = QFileDialog.getSaveFileName(self, 'Save Timetable PDF', self.get_download_path('pdf'), 'PDF Files (*.pdf)')
        if not save_path:
            return
        try:
            from reportlab.lib.pagesizes import letter, landscape, A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            doc = SimpleDocTemplate(save_path, pagesize=landscape(A4), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
            elements = []
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, alignment=1, textColor=colors.HexColor('#1E293B'), spaceAfter=6)
            sub_style = ParagraphStyle('DocSub', parent=styles['Normal'], fontName='Helvetica', fontSize=11, alignment=1, textColor=colors.HexColor('#64748B'), spaceAfter=14)
            title_txt = f'Academic Timetable — {self.target_combo.currentText()}'
            elements.append(Paragraph(title_txt, title_style))
            elements.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')} • Smart Timetable System", sub_style))
            headers = ['Day Order', 'Period 1', 'Period 2', 'Period 3', 'Period 4', 'Period 5']
            table_data = [headers]
            slot_map = {(r[0], r[1]): r for r in self.current_timetable_data}
            for day in range(1, 7):
                row = [f'Day Order {day}']
                for p in range(1, 6):
                    s = slot_map.get((day, p))
                    if s:
                        if self.current_mode == 'class':
                            row.append(f'{s[3]}\n{s[4]}\n({s[5]})')
                        else:
                            sem_str = f' (Sem {s[6]})' if len(s) > 6 and s[6] else ''
                            row.append(f'{s[4]}\n{s[5]}\n({s[3]}{sem_str})')
                    else:
                        row.append('FREE PERIOD')
                table_data.append(row)
            pdf_table = Table(table_data, colWidths=[90, 140, 140, 140, 140, 140])
            pdf_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, 0), 9), ('BOTTOMPADDING', (0, 0), (-1, 0), 8), ('TOPPADDING', (0, 0), (-1, 0), 8), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')), ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#F1F5F9')), ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'), ('FONTSIZE', (0, 1), (-1, -1), 8)]))
            elements.append(pdf_table)
            doc.build(elements)
            QMessageBox.information(self, 'PDF Exported', f'Timetable PDF exported successfully!\n\nSaved to:\n{save_path}')
        except Exception as e:
            QMessageBox.critical(self, 'Export Error', f'Failed to generate PDF:\n{e}')

    def export_csv(self):
        if not self.current_timetable_data:
            QMessageBox.warning(self, 'Export CSV', 'No timetable schedule available to export.')
            return
        save_path, _ = QFileDialog.getSaveFileName(self, 'Save Timetable CSV', self.get_download_path('csv'), 'CSV Files (*.csv)')
        if not save_path:
            return
        try:
            with open(save_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Timetable Schedule', self.target_combo.currentText()])
                writer.writerow(['Exported At', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                writer.writerow([])
                writer.writerow(['Day Order', 'Period 1', 'Period 2', 'Period 3', 'Period 4', 'Period 5'])
                slot_map = {(r[0], r[1]): r for r in self.current_timetable_data}
                for day in range(1, 7):
                    row = [f'Day Order {day}']
                    for p in range(1, 6):
                        s = slot_map.get((day, p))
                        if s:
                            if self.current_mode == 'class':
                                row.append(f'{s[3]} - {s[4]} ({s[5]})')
                            else:
                                sem_str = f' (Sem {s[6]})' if len(s) > 6 and s[6] else ''
                                row.append(f'{s[4]} - {s[5]} ({s[3]}{sem_str})')
                        else:
                            row.append('FREE PERIOD')
                    writer.writerow(row)
            QMessageBox.information(self, 'CSV Exported', f'Timetable CSV exported successfully!\n\nSaved to:\n{save_path}')
        except Exception as e:
            QMessageBox.critical(self, 'Export Error', f'Failed to export CSV:\n{e}')

    def clear_all_timetables(self):
        confirm = QMessageBox.question(self, 'Confirm Clear Timetable', 'Are you sure you want to completely remove the generated timetable?\n\nThis will clear all scheduled slots across all classes.', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            success = clear_timetable()
            if success:
                QMessageBox.information(self, 'Cleared', 'Timetable data successfully removed.')
                self.load_timetable_grid()
            else:
                QMessageBox.critical(self, 'Error', 'Failed to clear timetable.')
if __name__ == '__main__':
    from database.database import create_tables
    from ui.theme import apply_theme
    create_tables()
    app = QApplication.instance() or QApplication(sys.argv)
    apply_theme()
    win = ViewTimetableWindow()
    win.show()
    sys.exit(app.exec())
