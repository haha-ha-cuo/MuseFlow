from extension import db

# 关联表：歌单 <-> 歌曲 (多对多)
playlist_songs = db.Table('playlist_songs',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id',ondelete='CASCADE'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id',ondelete='CASCADE'), primary_key=True)
)

class Playlist(db.Model):
    __tablename__ = 'playlist'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), default="Unknown") # 创建者/艺术家
    cover = db.Column(db.String(200))
    description = db.Column(db.String(200), default="Songs from your server.")
    coverUrl = db.Column(db.String(200), default=None)
    
    # 建立与 Song 的关系
    # lazy='dynamic' 允许我们在 playlist.songs 上进行进一步的查询过滤
    songs = db.relationship('Song', secondary=playlist_songs, backref=db.backref('playlists', lazy='dynamic'))

    def toDict(self):
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "cover": self.cover,
            "description": self.description,
            "coverUrl": self.coverUrl,
            # 如果需要返回歌曲数量，可以在这里添加
            # "song_count": self.songs.count()
        }
