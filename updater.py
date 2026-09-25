import sys
import socket
import urllib.request
import json
from PySide6.QtCore import QThread, Signal, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from manifest import MANIFEST

def is_online(timeout=2.0) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('8.8.8.8', 53))
        s.close()
        return True
    except Exception:
        try:
            req = urllib.request.Request('https://api.github.com', headers={'User-Agent': 'TimetableApp'})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status in [200, 301, 302, 403]
        except Exception:
            return False

def parse_version(v_str):
    try:
        clean = v_str.strip().lstrip('v').strip()
        parts = [int(p) for p in clean.split('.') if p.isdigit()]
        return tuple(parts) if parts else (0,)
    except Exception:
        return (0,)

def check_for_updates():
    if not is_online():
        return None
    try:
        repo = MANIFEST.get('github_repo', 'Tamil-kumaran-b-n/Timetable-Management')
        manifest_url = f'https://raw.githubusercontent.com/{repo}/main/manifest.json'
        req = urllib.request.Request(manifest_url, headers={'User-Agent': 'TimetableApp', 'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            if resp.status == 200:
                remote_data = json.loads(resp.read().decode('utf-8'))
                remote_ver = remote_data.get('version', '1.0.0')
                local_ver = MANIFEST.get('version', '1.0.0')
                if parse_version(remote_ver) > parse_version(local_ver):
                    return {
                        'update_available': True,
                        'latest_version': remote_ver,
                        'current_version': local_ver,
                        'release_url': remote_data.get('release_url') or f'https://github.com/{repo}/releases',
                        'app_name': remote_data.get('app_name', 'Smart Academic Timetable Management System')
                    }
                else:
                    return {
                        'update_available': False,
                        'latest_version': remote_ver,
                        'current_version': local_ver,
                        'release_url': remote_data.get('release_url') or f'https://github.com/{repo}/releases'
                    }
    except Exception:
        try:
            repo = MANIFEST.get('github_repo', 'Tamil-kumaran-b-n/Timetable-Management')
            releases_url = f'https://api.github.com/repos/{repo}/releases/latest'
            req = urllib.request.Request(releases_url, headers={'User-Agent': 'TimetableApp'})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                if resp.status == 200:
                    rel_data = json.loads(resp.read().decode('utf-8'))
                    remote_ver = rel_data.get('tag_name', '').lstrip('v')
                    local_ver = MANIFEST.get('version', '1.0.0')
                    if remote_ver and parse_version(remote_ver) > parse_version(local_ver):
                        return {
                            'update_available': True,
                            'latest_version': remote_ver,
                            'current_version': local_ver,
                            'release_url': rel_data.get('html_url') or f'https://github.com/{repo}/releases',
                            'app_name': MANIFEST.get('app_name', 'Smart Academic Timetable Management System')
                        }
        except Exception:
            pass
    return None

class UpdateCheckerThread(QThread):
    update_available = Signal(dict)
    no_update = Signal(dict)

    def __init__(self, manual=False, parent=None):
        super().__init__(parent)
        self.manual = manual

    def run(self):
        res = check_for_updates()
        if res is not None:
            if res.get('update_available'):
                self.update_available.emit(res)
            elif self.manual:
                self.no_update.emit(res)

class UpdateDialog(QDialog):
    def __init__(self, update_info, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.setWindowTitle('Update Available')
        self.setFixedSize(420, 240)
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(14)

        title = QLabel('New Version Available!')
        title.setObjectName('Heading')
        layout.addWidget(title)

        card = QFrame()
        card.setObjectName('Card')
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 12, 15, 12)
        card_layout.setSpacing(6)

        cur_v = self.update_info.get('current_version', '1.0.0')
        new_v = self.update_info.get('latest_version', '1.0.0')
        info_label = QLabel(f'Current Version: <b>{cur_v}</b><br>Latest Version: <b style="color: #2563EB;">{new_v}</b>')
        info_label.setObjectName('NoticeText')
        card_layout.addWidget(info_label)

        sub_label = QLabel('A new update is available on GitHub Releases.')
        sub_label.setObjectName('Secondary')
        card_layout.addWidget(sub_label)

        layout.addWidget(card)
        layout.addStretch()

        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)
        btn_box.addStretch()

        btn_later = QPushButton('Later')
        btn_later.setProperty('btnStyle', 'secondary')
        btn_later.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_later.setFixedWidth(90)
        btn_later.clicked.connect(self.reject)
        btn_box.addWidget(btn_later)

        btn_download = QPushButton('Download')
        btn_download.setProperty('btnStyle', 'primary')
        btn_download.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_download.setFixedWidth(110)
        btn_download.clicked.connect(self.download_update)
        btn_box.addWidget(btn_download)

        layout.addLayout(btn_box)

    def download_update(self):
        url = self.update_info.get('release_url') or f"https://github.com/{MANIFEST.get('github_repo', 'Tamil-kumaran-b-n/Timetable-Management')}/releases"
        QDesktopServices.openUrl(QUrl(url))
        self.accept()
