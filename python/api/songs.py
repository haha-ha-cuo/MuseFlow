import os
from flask import jsonify, request, current_app
from model.Song import Song
from extension import db
from . import songs_bp

# DELETE /api/songs/<id>
@songs_bp.route('/<int:id>', methods=['DELETE'])
def deleteSong(id):
    try:
        song = db.session.get(Song, id)
        if not song:
            return jsonify({"code": 404, "msg": "Song not found"}), 404

        # 1. 获取文件路径
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], song.source)
        cover_path = None
        if song.coverSource:
            cover_path = os.path.join(current_app.config['COVER_FOLDER'], song.coverSource)
        
        # 2. 先删数据库 (Commit)
        db.session.delete(song)
        db.session.commit()
        
        # 3. 再尝试删文件 (允许失败)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as file_error:
                print(f"Warning: Failed to delete file {file_path}: {file_error}")

        if cover_path and os.path.exists(cover_path):
            try:
                os.remove(cover_path)
            except Exception as file_error:
                print(f"Warning: Failed to delete cover {cover_path}: {file_error}")
    
        return jsonify({"code": 200, "msg": "Deleted successfully"})
        
    except Exception as e:
        db.session.rollback()
        print(f"Delete Error: {e}")
        return jsonify({"code": 500, "msg": str(e)}), 500

# PUT /api/songs/update/<id>
# TODO: Suggest changing to /api/songs/<id> with PUT method
@songs_bp.route('/update/<int:id>', methods=['PUT'])
def updateSong(id):
    data = request.json
    if not data or 'title' not in data or 'artist' not in data:
        return jsonify({"code": 400, "msg": "Missing required fields"}), 400
    
    song = db.session.get(Song, id)
    if not song:
        return jsonify({"code": 404, "msg": "Song not found"}), 404
    
    song.title = data['title']
    song.artist = data['artist']
    if 'cover' in data:
        song.cover = data['cover']
        
    db.session.commit()
    
    return jsonify({
        "code": 200,
        "msg": "Song updated successfully",
        "data": song.toDict()
    })