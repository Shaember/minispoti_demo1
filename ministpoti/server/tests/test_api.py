import unittest
from ..app import app, db
from ..models import Track
import json

class TestAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_get_tracks_empty(self):
        response = self.client.get('/tracks')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), [])
    
    def test_add_track(self):
        track_data = {
            'title': 'Test Track',
            'artist': 'Test Artist',
            'genre': 'Rock',
            'duration': 180
        }
        response = self.client.post(
            '/track',
            data=json.dumps(track_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['title'], track_data['title'])
        self.assertEqual(data['artist'], track_data['artist'])
    
    def test_add_track_missing_fields(self):
        track_data = {
            'title': 'Test Track',
            'artist': 'Test Artist'
        }
        response = self.client.post(
            '/track',
            data=json.dumps(track_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_get_stats(self):
        # Добавляем тестовые треки
        with app.app_context():
            track1 = Track(title='Track 1', artist='Artist 1', genre='Rock', duration=180)
            track2 = Track(title='Track 2', artist='Artist 1', genre='Rock', duration=240)
            track3 = Track(title='Track 3', artist='Artist 2', genre='Pop', duration=200)
            db.session.add_all([track1, track2, track3])
            db.session.commit()
        
        response = self.client.get('/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Проверяем топ жанров
        self.assertEqual(len(data['top_genres']), 2)
        self.assertEqual(data['top_genres'][0]['genre'], 'Rock')
        self.assertEqual(data['top_genres'][0]['count'], 2)
        
        # Проверяем любимого исполнителя
        self.assertEqual(data['favorite_artist'], 'Artist 1')

if __name__ == '__main__':
    unittest.main() 