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