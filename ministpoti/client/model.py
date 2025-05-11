import json
import os
from dataclasses import dataclass
from typing import List, Optional
from datetime import timedelta, datetime

@dataclass
class Track:
    id: Optional[int]
    title: str
    artist: str
    genre: str
    duration: int  # в секундах
    
    @property
    def formatted_duration(self) -> str:
        """Возвращает длительность в формате MM:SS"""
        return str(timedelta(seconds=self.duration))[2:]

class Playlist:
    def __init__(self, name: str):
        self.name = name
        self.tracks: List[Track] = []
    
    def add_track(self, track: Track) -> None:
        self.tracks.append(track)
    
    def remove_track(self, track_id: int) -> None:
        self.tracks = [t for t in self.tracks if t.id != track_id]
    
    @property
    def total_duration(self) -> int:
        return sum(track.duration for track in self.tracks)

class Favorites(Playlist):
    def __init__(self):
        super().__init__('Избранное')

    def get_top_genres(self, limit: int = 5) -> List[tuple[str, int]]:
        """Возвращает топ жанров по количеству треков"""
        genre_count = {}
        for track in self.tracks:
            genre_count[track.genre] = genre_count.get(track.genre, 0) + 1
        return sorted(genre_count.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_favorite_artist(self) -> Optional[str]:
        """Возвращает самого часто встречающегося исполнителя"""
        artist_count = {}
        for track in self.tracks:
            artist_count[track.artist] = artist_count.get(track.artist, 0) + 1
        if not artist_count:
            return None
        return max(artist_count.items(), key=lambda x: x[1])[0]

@dataclass
class User:
    username: str
    password: str
    created_at: str
    demo_expire: str
    avatar: Optional[str] = None

class UserManager:
    USERS_FILE = 'users.json'

    @staticmethod
    def load_users():
        if not os.path.exists(UserManager.USERS_FILE):
            return {}
        with open(UserManager.USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def save_users(users):
        with open(UserManager.USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

    @staticmethod
    def register(username, password):
        users = UserManager.load_users()
        if username in users:
            return False, 'Пользователь уже существует'
        now = datetime.now().isoformat()
        demo_expire = (datetime.now() + timedelta(days=7)).isoformat()
        users[username] = {
            'password': password,
            'created_at': now,
            'demo_expire': demo_expire,
            'avatar': None
        }
        UserManager.save_users(users)
        return True, 'Регистрация успешна'

    @staticmethod
    def login(username, password):
        users = UserManager.load_users()
        if username not in users:
            return False, 'Пользователь не найден'
        if users[username]['password'] != password:
            return False, 'Неверный пароль'
        return True, users[username] 