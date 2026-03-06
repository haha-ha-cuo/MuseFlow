import os
from tinytag import TinyTag
from model.Song import Song
from extension import db
from .file_service import FileService

class SongService:
    @staticmethod
    def create_song(file, cover_file, title, artist, playlist):
        """
        处理上传并创建歌曲记录
        """
        # 1. 保存音频文件
        filename, path, relative_url = FileService.save_file(file, 'UPLOAD_FOLDER', '.mp3')
        if not filename:
            raise ValueError("Audio file save failed")
            
        # 2. 提取元数据
        duration = None
        tag_artist = "Unknown Artist"
        try:
            tag = TinyTag.get(path)
            if tag:
                duration = int(tag.duration) if tag.duration else None
                tag_artist = tag.artist if tag.artist else "Unknown Artist"
                del tag
        except Exception as e:
            print(f"Metadata warning: {e}")
            
        # 如果用户没填 artist，尝试用 tag 里的
        final_artist = artist if artist and artist != 'User' else tag_artist

        # 3. 保存封面 (如果有)
        cover_url = None
        cover_filename = None
        if cover_file:
            c_name, _, c_url = FileService.save_file(cover_file, 'COVER_FOLDER', '.jpg')
            cover_url = c_url
            cover_filename = c_name
            
        # 4. 创建数据库记录
        # 注意：这里我们只存相对路径或者需要拼接 host 的部分由 Controller 处理？
        # 为了方便，Service 层通常处理纯数据。
        # 之前的代码里 Song.url 存的是完整 URL (http://...)
        # 我们可以让 Service 返回对象，Controller 负责序列化和 URL 拼接
        
        newSong = Song(
            title=title,
            artist=final_artist,
            cover=cover_url, # 这里暂时存相对路径，Controller 里拼 host，或者 Song 模型里加 @property
            url=relative_url, 
            source=filename,
            duration=duration,
            coverSource=cover_filename
        )
        
        playlist.songs.append(newSong)
        db.session.commit()
        
        return newSong

    @staticmethod
    def delete_song(song_id):
        song = db.session.get(Song, song_id)
        if not song:
            return False
            
        # 1. 删除文件
        FileService.delete_file(song.source, 'UPLOAD_FOLDER')
        FileService.delete_file(song.coverSource, 'COVER_FOLDER')
        
        # 2. 删除记录
        db.session.delete(song)
        db.session.commit()
        return True
    
    @staticmethod
    def update_song(song_id, data):
        song = db.session.get(Song, song_id)
        if not song: return None
        
        if 'title' in data: song.title = data['title']
        if 'artist' in data: song.artist = data['artist']
        if 'cover' in data: song.cover = data['cover']
        
        db.session.commit()
        return song