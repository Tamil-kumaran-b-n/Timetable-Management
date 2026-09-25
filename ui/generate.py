import sys
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox, QRadioButton, QButtonGroup, QMessageBox, QFrame, QScrollArea, QProgressBar, QTextEdit
from database.database import get_all_classes
from database.workload import get_all_workloads
from database.generator import generate_timetable, get_all_timetable

class GenerateTimetableWindow(QWidget):

    def __init__(self, parent=None, container=None, navigate=None):
        super().__init__(container if container else parent)
        self.parent_window = parent
        self.embedded = container is not None
        self.navigate = navigate
        self.classes_data = []
        self.selected_class_id = None
        if not self.embedded:
            self.setWindowTitle('Generate Timetable - Smart Academic Timetable Management System')
            self.resize(1050, 700)
            self.setMinimumSize(900, 600)
        self.setup_ui()
        self.load_classes_dropdown()
        self.load_workload_summary()
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
        lbl_title = QLabel('Generate Timetable')
        lbl_title.setObjectName('Heading')
        lbl_sub = QLabel('Create timetables for all classes or a selected class')
        lbl_sub.setObjectName('Secondary')
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        self.btn_view_tt = QPushButton('View Timetable')
        self.btn_view_tt.setProperty('btnStyle', 'secondary')
        self.btn_view_tt.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_view_tt.clicked.connect(self.go_to_view_timetable)
        header_layout.addWidget(self.btn_view_tt)
        main_layout.addWidget(header_card)
        scope_card = QFrame()
        scope_card.setObjectName('Card')
        scope_layout = QVBoxLayout(scope_card)
        scope_layout.setContentsMargins(25, 20, 25, 25)
        scope_layout.setSpacing(14)
        lbl_scope_title = QLabel('1. Scope & Mode')
        lbl_scope_title.setObjectName('Subheading')
        scope_layout.addWidget(lbl_scope_title)
        lbl_scope_type = QLabel('Scope:')
        lbl_scope_type.setObjectName('FormLabel')
        scope_layout.addWidget(lbl_scope_type)
        scope_opts_layout = QHBoxLayout()
        scope_opts_layout.setSpacing(25)
        self.radio_all = QRadioButton('All Classes')
        self.radio_all.setChecked(True)
        self.radio_all.toggled.connect(self.on_scope_changed)
        self.radio_single = QRadioButton('Single Class')
        self.radio_single.toggled.connect(self.on_scope_changed)
        self.scope_group = QButtonGroup(self)
        self.scope_group.addButton(self.radio_all)
        self.scope_group.addButton(self.radio_single)
        scope_opts_layout.addWidget(self.radio_all)
        scope_opts_layout.addWidget(self.radio_single)
        scope_opts_layout.addStretch()
        scope_layout.addLayout(scope_opts_layout)
        self.class_select_container = QWidget()
        cls_sel_layout = QHBoxLayout(self.class_select_container)
        cls_sel_layout.setContentsMargins(0, 0, 0, 0)
        lbl_tgt = QLabel('Class:')
        lbl_tgt.setObjectName('FormLabel')
        cls_sel_layout.addWidget(lbl_tgt)
        self.class_combo = QComboBox()
        self.class_combo.setMinimumWidth(300)
        self.class_combo.currentIndexChanged.connect(self.on_class_combo_changed)
        cls_sel_layout.addWidget(self.class_combo)
        cls_sel_layout.addStretch()
        self.class_select_container.setVisible(False)
        scope_layout.addWidget(self.class_select_container)
        lbl_mode_type = QLabel('Mode:')
        lbl_mode_type.setObjectName('FormLabel')
        scope_layout.addWidget(lbl_mode_type)
        mode_opts_layout = QHBoxLayout()
        mode_opts_layout.setSpacing(25)
        self.radio_efficient = QRadioButton('Efficient (Balanced)')
        self.radio_efficient.setChecked(True)
        self.radio_random = QRadioButton('Random')
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.radio_efficient)
        self.mode_group.addButton(self.radio_random)
        mode_opts_layout.addWidget(self.radio_efficient)
        mode_opts_layout.addWidget(self.radio_random)
        mode_opts_layout.addStretch()
        scope_layout.addLayout(mode_opts_layout)
        main_layout.addWidget(scope_card)
        stats_card = QFrame()
        stats_card.setObjectName('Card')
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(25, 20, 25, 25)
        stats_layout.setSpacing(15)
        lbl_stats_title = QLabel('2. Workloads')
        lbl_stats_title.setObjectName('Subheading')
        stats_layout.addWidget(lbl_stats_title)
        grid_stats = QGridLayout()
        grid_stats.setSpacing(15)
        grid_stats.setColumnStretch(0, 1)
        grid_stats.setColumnStretch(1, 1)
        grid_stats.setColumnStretch(2, 1)
        self.stat_workloads = self.create_metric_card('Workloads', '0', 0, 0, grid_stats)
        self.stat_generated = self.create_metric_card('Generated', '0', 0, 1, grid_stats)
        self.stat_periods = self.create_metric_card('Periods', '0', 0, 2, grid_stats)
        stats_layout.addLayout(grid_stats)
        self.status_label = QLabel('Checking workloads...')
        self.status_label.setObjectName('NoticeText')
        self.status_label.setStyleSheet('font-weight: 600; margin-top: 5px;')
        stats_layout.addWidget(self.status_label)
        main_layout.addWidget(stats_card)
        exec_card = QFrame()
        exec_card.setObjectName('Card')
        exec_layout = QVBoxLayout(exec_card)
        exec_layout.setContentsMargins(25, 20, 25, 25)
        exec_layout.setSpacing(15)
        lbl_exec_title = QLabel('3. Generate')
        lbl_exec_title.setObjectName('Subheading')
        exec_layout.addWidget(lbl_exec_title)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)
        exec_layout.addWidget(self.progress_bar)
        btn_action_layout = QHBoxLayout()
        btn_action_layout.setSpacing(12)
        self.btn_generate = QPushButton('Generate')
        self.btn_generate.setProperty('btnStyle', 'primary')
        self.btn_generate.setMinimumHeight(42)
        self.btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_generate.clicked.connect(self.generate)
        btn_action_layout.addWidget(self.btn_generate)
        self.btn_refresh = QPushButton('Refresh')
        self.btn_refresh.setProperty('btnStyle', 'secondary')
        self.btn_refresh.setMinimumHeight(42)
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.load_workload_summary)
        btn_action_layout.addWidget(self.btn_refresh)
        btn_action_layout.addStretch()
        exec_layout.addLayout(btn_action_layout)
        main_layout.addWidget(exec_card)
        main_layout.addStretch()

    def create_metric_card(self, title, initial_val, row, col, grid_layout):
        card = QFrame()
        card.setObjectName('MetricCard')
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(4)
        lbl_v = QLabel(initial_val)
        lbl_v.setObjectName('MetricValue')
        lbl_t = QLabel(title)
        lbl_t.setObjectName('MetricLabel')
        layout.addWidget(lbl_v)
        layout.addWidget(lbl_t)
        grid_layout.addWidget(card, row, col)
        return lbl_v

    def load_classes_dropdown(self):
        self.classes_data = get_all_classes() or []
        self.class_combo.clear()
        for c in self.classes_data:
            cid = c[0]
            cname = c[1]
            sem = c[3] if len(c) > 3 else ''
            dept = c[2] if len(c) > 2 else ''
            self.class_combo.addItem(f'{cname} (Sem {sem}, {dept})', cid)

    def on_scope_changed(self):
        is_single = self.radio_single.isChecked()
        self.class_select_container.setVisible(is_single)
        if is_single and self.class_combo.count() > 0:
            self.selected_class_id = self.class_combo.currentData()
        else:
            self.selected_class_id = None
        self.load_workload_summary()

    def on_class_combo_changed(self):
        if self.radio_single.isChecked():
            self.selected_class_id = self.class_combo.currentData()
            self.load_workload_summary()

    def load_workload_summary(self):
        try:
            from database.database import get_connection
            workloads = get_all_workloads() or []
            if self.selected_class_id is not None:
                workloads = [w for w in workloads if len(w) > 4 and w[4] == self.selected_class_id or (len(w) > 2 and w[2] == self.selected_class_id)]
            total = len(workloads)
            total_periods = sum((int(row[13]) for row in workloads if len(row) > 13 and str(row[13]).isdigit()))
            conn = get_connection()
            try:
                c = conn.cursor()
                if self.selected_class_id:
                    c.execute('SELECT COUNT(DISTINCT class_id) FROM timetable WHERE class_id = ?', (self.selected_class_id,))
                else:
                    c.execute('SELECT COUNT(DISTINCT class_id) FROM timetable')
                gen_count = c.fetchone()[0] or 0
            finally:
                conn.close()
            self.stat_workloads.setText(str(total))
            self.stat_generated.setText(str(gen_count))
            self.stat_periods.setText(str(total_periods))
            scope_desc = 'for selected class' if self.selected_class_id else 'across all classes'
            if total == 0:
                self.status_label.setText(f'No workloads found {scope_desc}. Please add workloads first.')
                self.btn_generate.setEnabled(False)
            else:
                self.status_label.setText(f'{total} workload(s) ready ({total_periods} periods).')
                self.btn_generate.setEnabled(True)
        except Exception as error:
            self.status_label.setText(f'Error loading workloads: {error}')
            self.btn_generate.setEnabled(False)

    def load_data(self):
        self.load_workload_summary()

    def generate(self):
        workloads = get_all_workloads() or []
        if self.selected_class_id is not None:
            workloads = [w for w in workloads if len(w) > 4 and w[4] == self.selected_class_id or (len(w) > 2 and w[2] == self.selected_class_id)]
        if not workloads:
            QMessageBox.warning(self, 'No Workload', 'No workload found. Please assign workload first.')
            return
        scope_msg = 'Regenerate timetable for this class?' if self.selected_class_id is not None else 'Generate timetable for ALL classes?\n\nExisting timetables will be replaced.'
        confirm = QMessageBox.question(self, 'Confirm', scope_msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self.btn_generate.setEnabled(False)
        self.btn_generate.setText('Generating...')
        self.btn_refresh.setEnabled(False)
        self.status_label.setText('Generating timetable...')
        self.progress_bar.setValue(35)
        QApplication.processEvents()
        try:
            self.progress_bar.setValue(70)
            QApplication.processEvents()
            mode = 'random' if self.radio_random.isChecked() else 'efficient'
            mode_desc = 'Random' if mode == 'random' else 'Efficient'
            self.status_label.setText(f'Generating ({mode_desc} mode)...')
            result = generate_timetable(target_class_id=self.selected_class_id, mode=mode)
            if result:
                timetable = get_all_timetable() or []
                self.progress_bar.setValue(100)
                self.status_label.setText('Done! Timetable generated.')
                succ_msg = f'Timetable generated ({mode_desc} mode).' if self.selected_class_id is not None else f'All timetables generated ({mode_desc} mode).'
                self.load_workload_summary()
                QMessageBox.information(self, 'Success', succ_msg)
            else:
                self.progress_bar.setValue(0)
                self.status_label.setText('Generation failed.')
                QMessageBox.critical(self, 'Failed', 'Could not generate timetable. Please check workload constraints.')
        except ValueError as error:
            self.progress_bar.setValue(0)
            self.status_label.setText('Generation error.')
            QMessageBox.critical(self, 'Error', f'{error}')
        except Exception as error:
            self.progress_bar.setValue(0)
            self.status_label.setText('Unexpected error.')
            QMessageBox.critical(self, 'Error', f'{error}')
        finally:
            self.btn_generate.setEnabled(True)
            self.btn_generate.setText('Generate')
            self.btn_refresh.setEnabled(True)

    def go_to_view_timetable(self):
        if self.navigate:
            self.navigate('view_timetable')
if __name__ == '__main__':
    from database.database import create_tables
    from ui.theme import apply_theme
    create_tables()
    app = QApplication.instance() or QApplication(sys.argv)
    apply_theme()
    win = GenerateTimetableWindow()
    win.show()
    sys.exit(app.exec())
