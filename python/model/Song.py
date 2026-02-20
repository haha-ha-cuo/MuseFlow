from extension import db

class Song(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    cover = db.Column(db.String(200), nullable=True)
    url = db.Column(db.String(200), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)

    def toDict(self):
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "cover": self.cover,
            "url": self.url,
            "source": self.source,
            "duration": self.duration
        }