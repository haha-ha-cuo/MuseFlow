import os
import uuid
from flask import request, current_app
from model.PlayList import Playlist
from extension import db
from services.file_service import FileService
from . import playlists_bp
from utils.response import success, error

# GET /api/playlists
@playlists_bp.route('/', methods=['GET'])
def getPlaylists():
    playlists = Playlist.query.all()
    if not playlists:
        default_playlist = Playlist(
            title="My Playlist",
            artist="first list",
            cover=None,
            description="Songs from your server."
        )
        db.session.add(default_playlist)
        db.session.commit()
        playlists = [default_playlist]
    
    return success(data=[p.toDict() for p in playlists])

# GET /api/playlists/id=<id>
# TODO: Suggest changing to /api/playlists/<id> later
@playlists_bp.route('/<int:id>', methods=['GET'])
def getPlaylistDetail(id):
    playlist = db.session.get(Playlist, id)
    if not playlist:
        return error("Playlist not found", 404)
     
    songList = [song.toDict() for song in playlist.songs]
    
    return success(
        data=songList,
        title=playlist.title,
        description=playlist.description,
        cover=playlist.cover
    )

# POST /api/playlists/upload
@playlists_bp.route('/upload', methods=['POST'])
def createPlaylist():
    data = request.json
    if not data or 'title' not in data:
        return error("Missing required fields")

    new_playlist = Playlist(
        title=data['title'],
        artist=data.get('artist', 'User'),
        cover=data.get('cover'), 
        description=data.get('description', "Songs from your server."),
        coverSrc=None
    )
    db.session.add(new_playlist)
    db.session.commit()
    
    return success(msg="Playlist created successfully", data=new_playlist.toDict())

# PUT /api/playlists/update/<id>
@playlists_bp.route('/update/<int:id>', methods=['PUT'])
def updatePlaylist(id):
    data = request.json
    if not data or 'title' not in data or 'description' not in data:
        return error("Missing required fields")
    
    playlist = db.session.get(Playlist, id)
    if not playlist:
        return error("Playlist not found", 404)
    
    playlist.title = data['title']
    playlist.description = data['description']
    if 'cover' in data:
        playlist.cover = data['cover']
        
    db.session.commit()
    
    return success(msg="Playlist updated successfully", data=playlist.toDict())

# POST /api/playlists/upload/cover/<id>
@playlists_bp.route('/upload/cover/<int:id>', methods=['POST'])
def uploadPlaylistCover(id):
    if 'file' not in request.files:
        return error("No file part")
        
    file = request.files['file']
    if file.filename == '':
        return error("No selected file")
        
    ext = os.path.splitext(file.filename)[1]
    if not ext: ext = '.jpg'
        
    filename = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(current_app.config['COVER_FOLDER'], filename)
    file.save(save_path)

    cover_url = f"{request.host_url}static/cover/{filename}"
    
    playlist = db.session.get(Playlist, id)
    if not playlist:
        return error("Playlist not found", 404)
    if playlist.coverSrc:
        os.remove(os.path.join(current_app.config['COVER_FOLDER'], playlist.coverSrc))
    playlist.cover = cover_url 
    playlist.coverSrc = filename
    db.session.commit()
    
    return success(msg="Cover uploaded successfully", data={"coverUrl": cover_url})

@playlists_bp.route('/reset/cover/<int:id>', methods=['POST'])
def resetPlaylistCover(id):
    playlist = db.session.get(Playlist, id)
    if not playlist:
        return error("Playlist not found", 404)
    if playlist.coverSrc:
        FileService.delete_file(playlist.coverSrc, 'COVER_FOLDER')
    playlist.cover = None
    playlist.coverSrc = None
    db.session.commit()
    
    return success(msg="Cover reset successfully", data=playlist.toDict())

@playlists_bp.route('/delete/<int:id>', methods=['DELETE'])
def deletePlaylist(id):
    playlist = db.session.get(Playlist, id)
    if not playlist:
        return error("Playlist not found", 404)
    for song in playlist.songs:
        if song.coverSource:
            FileService.delete_file(song.coverSource, 'COVER_FOLDER')
        if song.source:
            FileService.delete_file(song.source, 'UPLOAD_FOLDER')
        db.session.delete(song)
        db.session.commit()
    if playlist.coverSrc:
        FileService.delete_file(playlist.coverSrc, 'COVER_FOLDER')
    db.session.delete(playlist)
    db.session.commit()
    
    return success(msg="Playlist deleted successfully")