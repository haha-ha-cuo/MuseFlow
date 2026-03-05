from extension import db

class Song(db.Model):
    __tablename__ = 'song'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    cover = db.Column(db.String(200), nullable=True)
    url = db.Column(db.String(200), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=True)
    coverSource = db.Column(db.String(200),nullable = True) 

    def toDict(self):
        # 将秒数转换为 MM:SS 格式
        formatted_duration = "0:00"
        if self.duration:
            minutes = self.duration // 60
            seconds = self.duration % 60
            formatted_duration = f"{minutes}:{seconds:02d}"

        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "cover": self.cover,
            "coverSource": self.coverSource,
            "url": self.url,
            "source": self.source,
            "duration": formatted_duration # 返回格式化后的字符串
        }