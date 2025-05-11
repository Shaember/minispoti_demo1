from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QTabWidget, QSpinBox, QHeaderView, QAbstractItemView, QComboBox, QInputDialog, QSlider, QDialog, QFormLayout, QFileDialog
)
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from typing import List
from .model import Track, UserManager
from .controller import MiniSpotifyController
import random
import requests
import os
from datetime import datetime
import sys
import json

PLAY_ICON = '▶'  # Можно заменить на SVG или PNG
PAUSE_ICON = '⏸'  # Можно заменить на SVG или PNG

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Вход в MiniSpotify')
        self.setModal(True)
        self.setFixedSize(350, 220)
        layout = QVBoxLayout(self)
        # Логотип
        logo = QLabel()
        logo.setPixmap(QPixmap(MainWindow.get_logo_pixmap(self)).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        title = QLabel('<span style="font-size:20px;font-weight:bold;color:#1db954;">MiniSpotify</span>')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        # Вкладка входа
        login_widget = QWidget()
        login_layout = QFormLayout(login_widget)
        self.login_username = QLineEdit()
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        login_layout.addRow('Логин:', self.login_username)
        login_layout.addRow('Пароль:', self.login_password)
        login_btn = QPushButton('Войти')
        login_btn.clicked.connect(self.try_login)
        login_layout.addRow(login_btn)
        self.login_msg = QLabel()
        login_layout.addRow(self.login_msg)
        self.tabs.addTab(login_widget, 'Вход')
        # Вкладка регистрации
        reg_widget = QWidget()
        reg_layout = QFormLayout(reg_widget)
        self.reg_username = QLineEdit()
        self.reg_password = QLineEdit()
        self.reg_password.setEchoMode(QLineEdit.Password)
        reg_layout.addRow('Логин:', self.reg_username)
        reg_layout.addRow('Пароль:', self.reg_password)
        reg_btn = QPushButton('Зарегистрироваться')
        reg_btn.clicked.connect(self.try_register)
        reg_layout.addRow(reg_btn)
        self.reg_msg = QLabel()
        reg_layout.addRow(self.reg_msg)
        self.tabs.addTab(reg_widget, 'Регистрация')
        self.user_data = None

    def try_login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text().strip()
        ok, data = UserManager.login(username, password)
        if ok:
            self.user_data = {'username': username, **data}
            self.accept()
        else:
            self.login_msg.setText(f'<span style="color:red">{data}</span>')

    def try_register(self):
        username = self.reg_username.text().strip()
        password = self.reg_password.text().strip()
        ok, msg = UserManager.register(username, password)
        if ok:
            self.reg_msg.setText(f'<span style="color:green">{msg}</span>')
        else:
            self.reg_msg.setText(f'<span style="color:red">{msg}</span>')

class MainWindow(QMainWindow):
    def __init__(self, controller: MiniSpotifyController):
        super().__init__()
        self.controller = controller
        self.playlists = {}
        self.player = QMediaPlayer()
        self.current_playing_row = None
        self.is_paused = False
        self.current_track = None
        self.current_user = None
        self.user_data_file = f'user_{os.getlogin()}.json'
        self.init_login()
        self.load_user_data()
        self.init_ui()
        self.load_tracks()
        self.set_dark_theme()
    
    def init_login(self):
        dlg = LoginDialog()
        if dlg.exec_() == QDialog.Accepted:
            self.current_user = dlg.user_data
        else:
            exit()

    def set_dark_theme(self):
        self.setStyleSheet('''
            QMainWindow { background: #181818; }
            QWidget { background: #181818; color: #fff; font-family: Arial; font-size: 14px; }
            QTabWidget::pane { border: none; }
            QTabBar::tab { background: #222; color: #bbb; padding: 8px 20px; border-radius: 8px 8px 0 0; }
            QTabBar::tab:selected { background: #1db954; color: #fff; }
            QTableWidget { background: #222; color: #fff; border: none; gridline-color: #333; selection-background-color: #1db954; selection-color: #fff; }
            QHeaderView::section { background: #181818; color: #1db954; font-weight: bold; border: none; }
            QPushButton { background: #1db954; color: #fff; border-radius: 8px; padding: 6px 16px; font-weight: bold; }
            QPushButton:hover { background: #1ed760; }
            QLineEdit, QSpinBox, QComboBox { background: #222; color: #fff; border: 1px solid #333; border-radius: 6px; padding: 4px; }
            QLabel { color: #fff; }
            QTableWidget::item:selected { background: #1db954; color: #fff; }
        ''')

    def set_light_theme(self):
        # Временно просто белый фон и чёрный текст
        self.setStyleSheet('''
            QMainWindow { background: #fff; }
            QWidget { background: #fff; color: #222; font-family: Arial; font-size: 14px; }
            QTabWidget::pane { border: none; }
            QTabBar::tab { background: #eee; color: #222; padding: 8px 20px; border-radius: 8px 8px 0 0; }
            QTabBar::tab:selected { background: #1db954; color: #fff; }
            QTableWidget { background: #fff; color: #222; border: none; gridline-color: #ccc; selection-background-color: #1db954; selection-color: #fff; }
            QHeaderView::section { background: #eee; color: #1db954; font-weight: bold; border: none; }
            QPushButton { background: #1db954; color: #fff; border-radius: 8px; padding: 6px 16px; font-weight: bold; }
            QPushButton:hover { background: #1ed760; }
            QLineEdit, QSpinBox, QComboBox { background: #fff; color: #222; border: 1px solid #ccc; border-radius: 6px; padding: 4px; }
            QLabel { color: #222; }
            QTableWidget::item:selected { background: #1db954; color: #fff; }
        ''')

    def init_ui(self):
        self.setWindowTitle('MiniSpotify')
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon(self.get_logo_pixmap()))
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        # Логотип и заголовок
        logo_layout = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(self.get_logo_pixmap().scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_layout.addWidget(logo)
        title = QLabel('<span style="font-size:28px;font-weight:bold;color:#1db954;">MiniSpotify</span>')
        logo_layout.addWidget(title)
        logo_layout.addStretch()
        user_label = QLabel(f"Пользователь: <b>{self.current_user['username']}</b>")
        user_label.setStyleSheet('color:#1db954; font-size:16px;')
        logo_layout.addWidget(user_label)
        main_layout.addLayout(logo_layout)
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        # --- Главная вкладка ---
        main_tab = QWidget()
        main_tab_layout = QHBoxLayout(main_tab)
        # Список плейлистов слева
        self.playlist_list = QTableWidget(0, 1)
        self.playlist_list.setHorizontalHeaderLabels(["Плейлисты"])
        self.playlist_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.playlist_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.playlist_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.playlist_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.playlist_list.setFixedWidth(220)
        main_tab_layout.addWidget(self.playlist_list)
        self.playlist_list.cellClicked.connect(self.on_playlist_selected)
        # Список треков справа
        self.main_tracks_table = QTableWidget(0, 5)
        self.main_tracks_table.setHorizontalHeaderLabels(["", "Название", "Исполнитель", "Жанр", "Длительность"])
        self.main_tracks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.main_tracks_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.main_tracks_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.main_tracks_table.setSelectionMode(QAbstractItemView.NoSelection)
        main_tab_layout.addWidget(self.main_tracks_table)
        # Кнопка для загрузки демо-треков
        demo_btn = QPushButton('Загрузить демо-треки')
        demo_btn.clicked.connect(self.load_demo_tracks)
        main_tab_layout.addWidget(demo_btn)
        tabs.addTab(main_tab, "Главная")
        self.update_playlist_list()
        self.update_main_tracks_table()
        # --- Вкладка 'Все треки' из открытых источников ---
        all_tracks_tab = QWidget()
        all_tracks_layout = QVBoxLayout(all_tracks_tab)
        self.all_tracks_table = QTableWidget(0, 5)
        self.all_tracks_table.setHorizontalHeaderLabels(["", "Название", "Исполнитель", "Жанр", "Длительность"])
        self.all_tracks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.all_tracks_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.all_tracks_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.all_tracks_table.setSelectionMode(QAbstractItemView.NoSelection)
        all_tracks_layout.addWidget(self.all_tracks_table)
        tabs.addTab(all_tracks_tab, "Все треки")
        self.load_all_tracks_from_api()
        # --- Вкладка Профиль (красиво оформленная) ---
        profile_tab = QWidget()
        profile_layout = QVBoxLayout(profile_tab)
        # Аватар
        avatar_layout = QHBoxLayout()
        self.avatar_label = QLabel()
        avatar_path = self.current_user.get('avatar')
        if avatar_path and os.path.exists(avatar_path):
            self.avatar_label.setPixmap(QPixmap(avatar_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.avatar_label.setPixmap(QPixmap(self.get_logo_pixmap()).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        avatar_layout.addWidget(self.avatar_label)
        avatar_btn = QPushButton('Сменить аватар')
        avatar_btn.clicked.connect(self.change_avatar)
        avatar_layout.addWidget(avatar_btn)
        avatar_layout.addStretch()
        profile_layout.addLayout(avatar_layout)
        # Имя и дата
        profile_layout.addWidget(QLabel(f"<h2>{self.current_user['username']}</h2>"))
        created = datetime.fromisoformat(self.current_user['created_at']).strftime('%d.%m.%Y %H:%M')
        profile_layout.addWidget(QLabel(f"Дата регистрации: <b>{created}</b>"))
        # Подписка
        demo_exp = datetime.fromisoformat(self.current_user['demo_expire'])
        left = (demo_exp - datetime.now()).days
        if left >= 0:
            profile_layout.addWidget(QLabel(f"<span style='color:#1db954'>Демо-подписка активна, осталось дней: <b>{left}</b></span>"))
        else:
            profile_layout.addWidget(QLabel(f"<span style='color:red'>Демо-подписка истекла</span>"))
        # Статистика
        profile_layout.addWidget(QLabel("<b>Статистика по избранному:</b>"))
        fav_tracks = self.playlists.get('Избранное', [])
        top_genres = self.controller.favorites.get_top_genres() if fav_tracks else []
        favorite_artist = self.controller.favorites.get_favorite_artist() if fav_tracks else None
        total_duration = sum(t.duration for t in fav_tracks)
        stats_text = "<b>Топ жанров:</b><br>"
        for genre, count in top_genres:
            stats_text += f"- {genre}: {count} треков<br>"
        stats_text += f"<br><b>Любимый исполнитель:</b> {favorite_artist or 'Нет данных'}"
        stats_text += f"<br><b>Общая длительность избранного:</b> {total_duration // 60} мин {total_duration % 60} сек"
        profile_layout.addWidget(QLabel(stats_text))
        # Настройки профиля
        settings_label = QLabel('<b>Настройки профиля:</b>')
        profile_layout.addWidget(settings_label)
        change_pass_btn = QPushButton('Сменить пароль')
        change_pass_btn.clicked.connect(self.change_password)
        profile_layout.addWidget(change_pass_btn)
        logout_btn = QPushButton('Выйти из аккаунта')
        logout_btn.clicked.connect(self.logout)
        profile_layout.addWidget(logout_btn)
        # Настройки плеера
        player_settings_label = QLabel('<b>Настройки плеера:</b>')
        profile_layout.addWidget(player_settings_label)
        theme_btn = QPushButton('Сменить тему')
        theme_btn.clicked.connect(self.toggle_theme)
        profile_layout.addWidget(theme_btn)
        volume_label = QLabel('Громкость:')
        profile_layout.addWidget(volume_label)
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_player_volume)
        profile_layout.addWidget(self.volume_slider)
        tabs.addTab(profile_tab, "Профиль")
        # --- Мини-плеер ---
        self.player_panel = QWidget()
        player_layout = QHBoxLayout(self.player_panel)
        self.player_panel.setStyleSheet('background:#181818; border-top:1px solid #222;')
        self.play_pause_btn = QPushButton(PLAY_ICON)
        self.play_pause_btn.setFixedSize(40, 40)
        self.play_pause_btn.setStyleSheet('background:#1db954; color:#fff; border-radius:20px; font-size:20px;')
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        player_layout.addWidget(self.play_pause_btn)
        self.track_info = QLabel('Трек не выбран')
        self.track_info.setStyleSheet('color:#fff; font-size:16px;')
        player_layout.addWidget(self.track_info)
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setStyleSheet('QSlider::groove:horizontal {background: #333; height: 6px; border-radius: 3px;} QSlider::handle:horizontal {background: #1db954; border: none; width: 16px; margin: -5px 0; border-radius: 8px;}')
        self.progress_slider.sliderMoved.connect(self.set_player_position)
        player_layout.addWidget(self.progress_slider)
        main_layout.addWidget(self.player_panel)
        self.player_panel.setFixedHeight(60)
        # Таймер для обновления прогресса
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        self.player.positionChanged.connect(self.on_position_changed)
        self.player.durationChanged.connect(self.on_duration_changed)

    def get_logo_pixmap(self):
        # Генерируем простую иконку в стиле Spotify (зелёный круг с белой нотой)
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        from PyQt5.QtGui import QPainter, QColor, QPen
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor('#1db954'))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 64, 64)
        painter.setPen(QPen(Qt.white, 4))
        painter.drawArc(18, 32, 28, 16, 30 * 16, 120 * 16)
        painter.drawArc(18, 40, 28, 12, 30 * 16, 120 * 16)
        painter.end()
        return pixmap

    def load_tracks(self):
        # Загружает треки в главную таблицу (по умолчанию — первый плейлист)
        self.main_tracks_table.setRowCount(0)
        pl_name = list(self.playlists.keys())[0] if self.playlists else None
        if not pl_name or pl_name not in self.playlists:
            return
        for track in self.playlists[pl_name]:
            self._add_track_to_table(self.main_tracks_table, track)

    def _add_track_to_table(self, table, track: Track, row_idx=None):
        row = table.rowCount() if row_idx is None else row_idx
        table.insertRow(row)
        # Play button/icon
        play_btn = QPushButton(PLAY_ICON)
        play_btn.setStyleSheet('background:transparent; color:#1db954; font-size:18px; border:none;')
        play_btn.setCursor(Qt.PointingHandCursor)
        play_btn.clicked.connect(lambda _, t=track, r=row: self.toggle_play(t, table, r))
        table.setCellWidget(row, 0, play_btn)
        table.setItem(row, 1, QTableWidgetItem(track.title))
        table.setItem(row, 2, QTableWidgetItem(track.artist))
        table.setItem(row, 3, QTableWidgetItem(track.genre))
        table.setItem(row, 4, QTableWidgetItem(track.formatted_duration))
        # Hover-эффект
        table.setRowHeight(row, 36)

    def is_demo_active(self):
        demo_exp = datetime.fromisoformat(self.current_user['demo_expire'])
        return (demo_exp - datetime.now()).days >= 0

    def toggle_play(self, track: Track, table, row):
        if not self.is_demo_active():
            QMessageBox.warning(self, 'Демо-подписка', 'Ваша демо-подписка истекла. Прослушивание недоступно.')
            return
        # Снимаем иконку Pause с других строк
        for r in range(table.rowCount()):
            btn = table.cellWidget(r, 0)
            if btn:
                btn.setText(PLAY_ICON)
        btn = table.cellWidget(row, 0)
        if self.current_playing_row == row and not self.is_paused:
            self.player.pause()
            btn.setText(PLAY_ICON)
            self.is_paused = True
        else:
            if hasattr(track, 'mp3_url') and track.mp3_url:
                self.player.setMedia(QMediaContent(QUrl(track.mp3_url)))
                self.player.play()
            else:
                QMessageBox.information(self, 'Воспроизведение', 'Аудио для этого трека недоступно в демо-версии.')
                return
            btn.setText(PAUSE_ICON)
            self.current_playing_row = row
            self.is_paused = False
        self.highlight_row(table, row)
        self.current_track = track
        self.update_player_panel(track)

    def highlight_row(self, table, row):
        for r in range(table.rowCount()):
            for c in range(table.columnCount()):
                item = table.item(r, c)
                if item:
                    item.setBackground(Qt.transparent)
        for c in range(table.columnCount()):
            item = table.item(row, c)
            if item:
                item.setBackground(Qt.green)

    def add_track(self):
        title = self.title_input.text().strip()
        artist = self.artist_input.text().strip()
        genre = self.genre_input.text().strip()
        duration = self.duration_input.value()
        if not all([title, artist, genre, duration]):
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')
            return
        track = Track(None, title, artist, genre, duration)
        if self.controller.add_track(track):
            self.load_tracks()
            self.title_input.clear()
            self.artist_input.clear()
            self.genre_input.clear()
            self.duration_input.setValue(1)
        else:
            QMessageBox.warning(self, 'Ошибка', 'Не удалось добавить трек')

    def add_to_favorites(self):
        row = self.main_tracks_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, 'Ошибка', 'Выберите трек')
            return
        title = self.main_tracks_table.item(row, 1).text()
        artist = self.main_tracks_table.item(row, 2).text()
        genre = self.main_tracks_table.item(row, 3).text()
        duration = self.main_tracks_table.item(row, 4).text()
        duration_sec = sum(int(x) * 60 ** i for i, x in enumerate(reversed(duration.split(':')))) if ':' in duration else int(duration)
        track = Track(None, title, artist, genre, duration_sec)
        if track not in self.playlists['Избранное']:
            self.playlists['Избранное'].append(track)
            self.save_user_data()
            self.update_main_tracks_table()

    def remove_from_favorites(self):
        pl_name = 'Избранное'
        row = self.main_tracks_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, 'Ошибка', 'Выберите трек')
            return
        title = self.main_tracks_table.item(row, 1).text()
        artist = self.main_tracks_table.item(row, 2).text()
        genre = self.main_tracks_table.item(row, 3).text()
        duration = self.main_tracks_table.item(row, 4).text()
        duration_sec = sum(int(x) * 60 ** i for i, x in enumerate(reversed(duration.split(':')))) if ':' in duration else int(duration)
        track = Track(None, title, artist, genre, duration_sec)
        self.playlists[pl_name] = [t for t in self.playlists[pl_name] if not (
            t.title == track.title and t.artist == track.artist and t.genre == track.genre and t.duration == track.duration
        )]
        self.save_user_data()
        self.update_main_tracks_table()

    def update_playlist_table(self):
        pl_name = self.playlist_combo.currentText()
        self.playlist_table.setRowCount(0)
        if not pl_name or pl_name not in self.playlists:
            return
        for track in self.playlists[pl_name]:
            self._add_track_to_table(self.playlist_table, track)

    def toggle_play_pause(self):
        if not self.is_demo_active():
            QMessageBox.warning(self, 'Демо-подписка', 'Ваша демо-подписка истекла. Прослушивание недоступно.')
            return
        if not self.current_track:
            return
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.play_pause_btn.setText(PLAY_ICON)
        else:
            if hasattr(self.current_track, 'mp3_url') and self.current_track.mp3_url:
                self.player.play()
                self.play_pause_btn.setText(PAUSE_ICON)
            else:
                QMessageBox.information(self, 'Воспроизведение', 'Аудио для этого трека недоступно в демо-версии.')

    def update_player_panel(self, track: Track):
        self.track_info.setText(f"{track.title} — {track.artist}")
        if hasattr(track, 'mp3_url') and track.mp3_url:
            self.play_pause_btn.setEnabled(True)
            self.progress_slider.setEnabled(True)
            self.progress_timer.start(500)
        else:
            self.play_pause_btn.setEnabled(False)
            self.progress_slider.setEnabled(False)
            self.progress_timer.stop()
            self.progress_slider.setValue(0)

    def update_progress(self):
        if self.player.duration() > 0:
            pos = int(self.player.position() * 100 / self.player.duration())
            self.progress_slider.setValue(pos)

    def set_player_position(self, pos):
        if self.player.duration() > 0:
            self.player.setPosition(int(pos * self.player.duration() / 100))

    def on_position_changed(self, position):
        if self.player.duration() > 0:
            pos = int(position * 100 / self.player.duration())
            self.progress_slider.setValue(pos)

    def on_duration_changed(self, duration):
        self.progress_slider.setValue(0)

    def logout(self):
        QMessageBox.information(self, 'Выход', 'Выход из аккаунта...')
        os.execl(sys.executable, sys.executable, *sys.argv)

    def load_user_data(self):
        # Загружаем плейлисты и избранное для пользователя
        if os.path.exists(self.user_data_file):
            with open(self.user_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.playlists = {k: [Track(**t) for t in v] for k, v in data.get('playlists', {}).items()}
        else:
            self.playlists = {'Избранное': []}

    def save_user_data(self):
        # Сохраняем плейлисты и избранное для пользователя
        data = {
            'playlists': {k: [t.__dict__ for t in v] for k, v in self.playlists.items()}
        }
        with open(self.user_data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_demo_tracks(self):
        # Статичные демо-треки
        demo_tracks = [
            Track(None, "Shape of You", "Ed Sheeran", "Pop", 235),
            Track(None, "Blinding Lights", "The Weeknd", "Pop", 200),
            Track(None, "Dance Monkey", "Tones and I", "Pop", 210),
            Track(None, "Someone You Loved", "Lewis Capaldi", "Pop", 182),
            Track(None, "Bad Guy", "Billie Eilish", "Pop", 194)
        ]
        # Добавляем треки в контроллер
        for track in demo_tracks:
            self.controller.add_track(track)
        # Добавляем в избранное, если оно пустое
        if not self.playlists.get('Избранное'):
            self.playlists['Избранное'] = demo_tracks.copy()
            self.save_user_data()
        # Обновляем таблицы
        self.load_tracks()
        self.load_all_tracks_from_api()
        QMessageBox.information(self, 'Успех', 'Демо-треки добавлены!')

    def create_playlist(self):
        name, ok = QInputDialog.getText(self, 'Создать плейлист', 'Название плейлиста:')
        if ok and name:
            if name in self.playlists:
                QMessageBox.warning(self, 'Ошибка', 'Плейлист с таким именем уже существует')
                return
            self.playlists[name] = []
            self.playlist_combo.addItem(name)
            self.playlist_combo.setCurrentText(name)

    def add_track_to_playlist(self):
        pl_name = self.playlist_combo.currentText()
        if not pl_name:
            QMessageBox.warning(self, 'Ошибка', 'Выберите плейлист')
            return
        row = self.tracks_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, 'Ошибка', 'Выберите трек')
            return
        title = self.tracks_table.item(row, 1).text()
        artist = self.tracks_table.item(row, 2).text()
        genre = self.tracks_table.item(row, 3).text()
        duration = self.tracks_table.item(row, 4).text()
        duration_sec = sum(int(x) * 60 ** i for i, x in enumerate(reversed(duration.split(':')))) if ':' in duration else int(duration)
        track = Track(None, title, artist, genre, duration_sec)
        if track not in self.playlists[pl_name]:
            self.playlists[pl_name].append(track)
            self.update_playlist_table()

    def remove_from_playlist(self):
        pl_name = self.playlist_combo.currentText()
        if not pl_name:
            QMessageBox.warning(self, 'Ошибка', 'Выберите плейлист')
            return
        row = self.playlist_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, 'Ошибка', 'Выберите трек')
            return
        title = self.playlist_table.item(row, 1).text()
        artist = self.playlist_table.item(row, 2).text()
        genre = self.playlist_table.item(row, 3).text()
        duration = self.playlist_table.item(row, 4).text()
        duration_sec = sum(int(x) * 60 ** i for i, x in enumerate(reversed(duration.split(':')))) if ':' in duration else int(duration)
        track = Track(None, title, artist, genre, duration_sec)
        self.playlists[pl_name] = [t for t in self.playlists[pl_name] if not (
            t.title == track.title and t.artist == track.artist and t.genre == track.genre and t.duration == track.duration
        )]
        self.update_playlist_table()

    def update_playlist_list(self):
        self.playlist_list.setRowCount(0)
        for i, name in enumerate(self.playlists.keys()):
            self.playlist_list.insertRow(i)
            self.playlist_list.setItem(i, 0, QTableWidgetItem(name))

    def on_playlist_selected(self, row, col):
        pl_name = self.playlist_list.item(row, 0).text()
        self.update_main_tracks_table(pl_name)

    def update_main_tracks_table(self, pl_name=None):
        if pl_name is None:
            pl_name = list(self.playlists.keys())[0] if self.playlists else None
        self.main_tracks_table.setRowCount(0)
        if not pl_name or pl_name not in self.playlists:
            return
        for track in self.playlists[pl_name]:
            self._add_track_to_table(self.main_tracks_table, track)

    def load_all_tracks_from_api(self):
        # Показываем те же демо-треки, что и на главной
        demo_tracks = [
            Track(None, "Shape of You", "Ed Sheeran", "Pop", 235),
            Track(None, "Blinding Lights", "The Weeknd", "Pop", 200),
            Track(None, "Dance Monkey", "Tones and I", "Pop", 210),
            Track(None, "Someone You Loved", "Lewis Capaldi", "Pop", 182),
            Track(None, "Bad Guy", "Billie Eilish", "Pop", 194)
        ]
        self.all_tracks_table.setRowCount(0)
        for i, track in enumerate(demo_tracks):
            self._add_track_to_table(self.all_tracks_table, track, i)

    def change_avatar(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Выберите аватар', '', 'Images (*.png *.jpg *.jpeg)')
        if path:
            self.current_user['avatar'] = path
            self.avatar_label.setPixmap(QPixmap(path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            users = UserManager.load_users()
            users[self.current_user['username']]['avatar'] = path
            UserManager.save_users(users)

    def change_password(self):
        new_pass, ok = QInputDialog.getText(self, 'Смена пароля', 'Введите новый пароль:')
        if ok and new_pass:
            users = UserManager.load_users()
            users[self.current_user['username']]['password'] = new_pass
            UserManager.save_users(users)
            QMessageBox.information(self, 'Успех', 'Пароль успешно изменён!')

    def toggle_theme(self):
        # Пример: просто инвертируем тему
        if hasattr(self, 'dark_theme') and not self.dark_theme:
            self.set_dark_theme()
            self.dark_theme = True
        else:
            self.set_light_theme()
            self.dark_theme = False

    def set_player_volume(self, value):
        self.player.setVolume(value) 