import unittest
from ..model import Track, Playlist, Favorites

class TestTrack(unittest.TestCase):
    def test_track_creation(self):
        track = Track(1, "Test Track", "Test Artist", "Rock", 180)
        self.assertEqual(track.title, "Test Track")
        self.assertEqual(track.artist, "Test Artist")
        self.assertEqual(track.genre, "Rock")
        self.assertEqual(track.duration, 180)
    
    def test_formatted_duration(self):
        track = Track(1, "Test Track", "Test Artist", "Rock", 125)
        self.assertEqual(track.formatted_duration, "02:05")

class TestPlaylist(unittest.TestCase):
    def setUp(self):
        self.playlist = Playlist("Test Playlist")
        self.track1 = Track(1, "Track 1", "Artist 1", "Rock", 180)
        self.track2 = Track(2, "Track 2", "Artist 2", "Pop", 240)
    
    def test_add_track(self):
        self.playlist.add_track(self.track1)
        self.assertEqual(len(self.playlist.tracks), 1)
        self.assertEqual(self.playlist.tracks[0], self.track1)
    
    def test_remove_track(self):
        self.playlist.add_track(self.track1)
        self.playlist.add_track(self.track2)
        self.playlist.remove_track(1)
        self.assertEqual(len(self.playlist.tracks), 1)
        self.assertEqual(self.playlist.tracks[0], self.track2)
    
    def test_total_duration(self):
        self.playlist.add_track(self.track1)
        self.playlist.add_track(self.track2)
        self.assertEqual(self.playlist.total_duration, 420)

class TestFavorites(unittest.TestCase):
    def setUp(self):
        self.favorites = Favorites()
        self.track1 = Track(1, "Track 1", "Artist 1", "Rock", 180)
        self.track2 = Track(2, "Track 2", "Artist 2", "Rock", 240)
        self.track3 = Track(3, "Track 3", "Artist 1", "Pop", 200)
    
    def test_add_track(self):
        self.favorites.add_track(self.track1)
        self.assertEqual(len(self.favorites.tracks), 1)
    
    def test_remove_track(self):
        self.favorites.add_track(self.track1)
        self.favorites.add_track(self.track2)
        self.favorites.remove_track(1)
        self.assertEqual(len(self.favorites.tracks), 1)
    
    def test_get_top_genres(self):
        self.favorites.add_track(self.track1)
        self.favorites.add_track(self.track2)
        self.favorites.add_track(self.track3)
        top_genres = self.favorites.get_top_genres()
        self.assertEqual(top_genres[0][0], "Rock")
        self.assertEqual(top_genres[0][1], 2)
    
    def test_get_favorite_artist(self):
        self.favorites.add_track(self.track1)
        self.favorites.add_track(self.track2)
        self.favorites.add_track(self.track3)
        self.assertEqual(self.favorites.get_favorite_artist(), "Artist 1")

if __name__ == '__main__':
    unittest.main() 