from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Track(db.Model):
    __tablename__ = 'tracks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'genre': self.genre,
            'duration': self.duration
        }

class Playlist(db.Model):
    __tablename__ = 'playlists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    tracks = db.relationship('Track', secondary='playlist_tracks')

class PlaylistTrack(db.Model):
    __tablename__ = 'playlist_tracks'
    
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'), primary_key=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    track = db.relationship('Track') 