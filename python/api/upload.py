import os
import uuid
from flask import jsonify, request, current_app
from model.PlayList import Playlist
from model.Song import Song
from tinytag import TinyTag
from extension import db
from . import upload_bp

# POST /api/upload/playlistId=<playlistId>
# TODO: This route is slightly awkward. Consider moving to /api/playlists/<id>/songs in the future.
@upload_bp.route('/<int:playlistId>/songs', methods=['POST'])
def uploadSong(playlistId):
    try:
        playlist = db.session.get(Playlist, playlistId)
    except Exception as e:
        return jsonify({"code": 500, "msg": "Database error", "error": str(e)}), 500
    
    if not playlist:
        return jsonify({"code": 404, "msg": "Playlist not found"}), 404

    if 'file' not in request.files:
        return jsonify({"code": 400, "msg": "No file part"}), 400

    if 'cover' in request.files:
        cover = request.files['cover']
    else:
        cover = None
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"code": 400, "msg": "No selected file"}), 400

    if file:
        ext = os.path.splitext(file.filename)[1]
        if not ext: ext = '.mp3'
            
        filename = f"{uuid.uuid4().hex}{ext}"
        
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        file_url = f"{request.host_url}static/music/{filename}"
        
        duration = None
        artist = "Unknown Artist"
        try:
            tag = TinyTag.get(save_path)
            if tag:
                duration = int(tag.duration) if tag.duration else None
                artist = tag.artist if tag.artist else "Unknown Artist"
                del tag
        except Exception as e:
            print(f"Metadata warning: {e}")
            
        cover_url = None
        if cover:
            cover_name = f"{uuid.uuid4().hex}{os.path.splitext(cover.filename)[1]}"
            cover_url = f"{request.host_url}static/cover/{cover_name}"
            cover.save(os.path.join(current_app.config['COVER_FOLDER'], cover_name))
        
        newSong = Song(
            title=request.form.get('name', 'Unknown Title'),
            artist=artist,
            cover=cover_url if cover else None,
            url=file_url,
            source=filename,
            duration=duration,
            coverSource=cover.filename if cover else None
        )

        playlist.songs.append(newSong)
        db.session.commit()

        print(f"Upload success: {newSong.toDict()}")

        return jsonify({
            "code": 200,
            "msg": "Upload successful",
            "data": newSong.toDict()
        })