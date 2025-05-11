import requests
from typing import List, Dict, Any
from .model import Track, Playlist, Favorites

class MiniSpotifyController:
    def __init__(self, api_url: str = "http://localhost:5000"):
        self.api_url = api_url
        self.favorites = Favorites()
        self.playlists: Dict[str, Playlist] = {}
    
    def get_all_tracks(self) -> List[Track]:
        """Получение всех треков с сервера"""
        response = requests.get(f"{self.api_url}/tracks")
        if response.status_code == 200:
            tracks_data = response.json()
            return [Track(**track) for track in tracks_data]
        return []
    
    def add_track(self, track: Track) -> bool:
        """Добавление нового трека на сервер"""
        response = requests.post(
            f"{self.api_url}/track",
            json={
                "title": track.title,
                "artist": track.artist,
                "genre": track.genre,
                "duration": track.duration
            }
        )
        return response.status_code == 200 or response.status_code == 201
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики с сервера"""
        response = requests.get(f"{self.api_url}/stats")
        if response.status_code == 200:
            return response.json()
        return {}
    
    def create_playlist(self, name: str) -> Playlist:
        """Создание нового плейлиста"""
        playlist = Playlist(name)
        self.playlists[name] = playlist
        return playlist
    
    def add_to_favorites(self, track: Track) -> None:
        """Добавление трека в избранное"""
        self.favorites.add_track(track)
    
    def remove_from_favorites(self, track: Track) -> None:
        """Удаление трека из избранного"""
        self.favorites.tracks = [t for t in self.favorites.tracks if not (
            t.title == track.title and t.artist == track.artist and t.genre == track.genre and t.duration == track.duration
        )]
    
    def get_top_genres(self, limit: int = 5) -> List[tuple[str, int]]:
        """Получение топ жанров из избранного"""
        return self.favorites.get_top_genres(limit)
    
    def get_favorite_artist(self) -> str:
        """Получение любимого исполнителя из избранного"""
        return self.favorites.get_favorite_artist()

    def get_total_favorites_duration(self) -> int:
        return sum(track.duration for track in self.favorites.tracks) 