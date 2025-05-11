from flask import Flask, request, jsonify
from .models import db, Track, Playlist, Favorite
from sqlalchemy import func
import os

# Инициализация Flask приложения
# TODO: Добавить конфигурацию для продакшена
app = Flask(__name__)

# Конфигурация базы данных
# Использую SQLite для простоты разработки
# В продакшене лучше использовать PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///minispotify.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db.init_app(app)

@app.route('/tracks', methods=['GET'])
def get_tracks():
    # Получаем все треки из базы данных
    # TODO: Добавить пагинацию для больших списков
    tracks = Track.query.all()
    return jsonify([track.to_dict() for track in tracks])

@app.route('/track', methods=['POST'])
def add_track():
    # Добавление нового трека
    # TODO: Добавить валидацию формата аудио файла
    data = request.json
    
    if not all(k in data for k in ['title', 'artist', 'genre', 'duration']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Создаем новый трек
    track = Track(
        title=data['title'],
        artist=data['artist'],
        genre=data['genre'],
        duration=data['duration']
    )
    
    # Сохраняем в базу данных
    db.session.add(track)
    db.session.commit()
    
    return jsonify(track.to_dict()), 201

@app.route('/stats', methods=['GET'])
def get_stats():
    # Получаем статистику по трекам
    # TODO: Добавить кэширование для оптимизации
    
    # Получаем топ жанров
    # Используем SQLAlchemy для агрегации данных
    top_genres = db.session.query(
        Track.genre,
        func.count(Track.id).label('count')
    ).group_by(Track.genre).order_by(func.count(Track.id).desc()).limit(5).all()
    
    # Получаем любимого исполнителя
    # TODO: Добавить фильтрацию по дате
    favorite_artist = db.session.query(
        Track.artist,
        func.count(Track.id).label('count')
    ).group_by(Track.artist).order_by(func.count(Track.id).desc()).first()
    
    return jsonify({
        'top_genres': [{'genre': g[0], 'count': g[1]} for g in top_genres],
        'favorite_artist': favorite_artist[0] if favorite_artist else None
    })

def init_db():
    # Инициализация базы данных
    # TODO: Добавить миграции
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    # Запуск приложения
    # TODO: Добавить логирование
    init_db()
    app.run(debug=True) 