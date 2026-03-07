from flask import request
from . import songs_bp
from utils.response import success, error
from services.song_service import SongService

# DELETE /api/songs/<id>
@songs_bp.route('/<int:id>', methods=['DELETE'])
def deleteSong(id):
    try:
        result = SongService.delete_song(id)
        if not result:
            return error("Song not found", 404)
        return success(msg="Deleted successfully")
    except Exception as e:
        return error(str(e), 500)

# PUT /api/songs/update/<id>
@songs_bp.route('/update/<int:id>', methods=['PUT'])
def updateSong(id):
    data = request.json
    if not data or 'title' not in data or 'artist' not in data:
        return error("Missing required fields")
    
    song = SongService.update_song(id, data)
    if not song:
        return error("Song not found", 404)
    
    return success(data=song.toDict(), msg="Song updated successfully")

# POST /api/songs/upload/cover/<id>
@songs_bp.route('/upload/cover/<int:id>', methods=['POST'])
def uploadSongCover(id):
    if 'file' not in request.files:
        return error("No file part")
        
    file = request.files['file']
    if file.filename == '':
        return error("No selected file")
        
    song, err = SongService.upload_cover(id, file)
    if err:
        return error(err, 404 if err == "Song not found" else 400)
        
    # 构建完整 URL (如果前端需要)
    # 这里保持和 create_song 一致，返回 relative URL 还是 absolute?
    # Song.toDict() returns self.cover directly.
    # If self.cover is relative (/static/...), frontend usually handles it if base URL is correct.
    # Or we can prepend request.host_url here for convenience.
    
    # Check if song.cover is relative
    cover_url = song.cover
    if cover_url and cover_url.startswith('/'):
        cover_url = f"{request.host_url.rstrip('/')}{cover_url}"
        
    return success(msg="Cover uploaded successfully", data={"coverUrl": cover_url})

@songs_bp.route('/reset/cover/<int:id>', methods=['POST'])
def resetSongCover(id):
    song, err = SongService.reset_cover(id)
    if err:
        return error(err, 404 if err == "Song not found" else 400)
    
    return success(msg="Cover reset successfully", data=song.toDict())
