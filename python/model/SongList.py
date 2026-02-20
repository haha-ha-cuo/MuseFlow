from model.Song import Song

class SongList:
    def __init__(self, id, title, artist, cover):
        self.id = id
        self.title = title
        self.cover = cover
        self.songs = []
    
    def getId(self):
        return self.id
    
    def getTitle(self):
        return self.title
    
    def getArtist(self):
        return self.artist
    
    def getCover(self):
        return self.cover
    
    def getUrl(self):
        return self.urls

    def setId(self, id):
        self.id = id
    
    def setTitle(self, title):
        self.title = title
    
    def setArtist(self, artist):
        self.artist = artist
    
    def setCover(self, cover):
        self.cover = cover
        
    def setUrl(self, url):
        self.url = urls
        
    def __str__(self):
        return f"SongList(id={self.id}, title={self.title}, artist={self.artist}, cover={self.cover}, urls={self.urls})"
