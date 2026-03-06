import os
from flask import request
from model.PlayList import Playlist
from extension import db
from . import upload_bp
from utils.response import success, error
from services.song_service import SongService

# POST /api/upload/<playlistId>/songs
@upload_bp.route('/<int:playlistId>/songs', methods=['POST'])
def uploadSong(playlistId):
    try:
        playlist = db.session.get(Playlist, playlistId)
    except Exception as e:
        return error("Database error: " + str(e), 500)
    
    if not playlist:
        return error("Playlist not found", 404)

    if 'file' not in request.files:
        return error("No file part")
        
    file = request.files['file']
    if file.filename == '':
        return error("No selected file")

    cover = request.files.get('cover')
    title = request.form.get('name', 'Unknown Title')
    artist = "User" # 这里暂时写死，Service 里会尝试从 tag 读取

    try:
        newSong = SongService.create_song(file, cover, title, artist, playlist)
        
        # SongService 存的是相对路径，我们需要在这里拼上 host_url
        # 或者最好让 toDict() 自己处理，或者 Service 返回时就处理好
        # 这里为了保持一致性，我们手动修正一下 url
        # (实际上如果前端有 BASE_URL 配置，相对路径也是可以的)
        
        # 修正: 之前的 SongService 里直接把 relative_url 存进了数据库
        # 如果前端依赖完整 URL，我们需要在这里做点什么，或者修改 Service
        # 暂时保持现状，让前端适配相对路径，或者我们在这里 hack 一下
        # newSong.url = f"{request.host_url}{newSong.url.lstrip('/')}"
        # newSong.cover = f"{request.host_url}{newSong.cover.lstrip('/')}" if newSong.cover else None
        
        # 最好的方式是让 Song.toDict() 动态拼接 host_url，但这需要 context
        # 这里为了兼容，我们在 Service 里保存时最好就保存完整 URL，或者在这里拼
        
        # 重新查看 SongService，它保存的是 /static/music/xxx.mp3
        # 之前的代码保存的是 http://localhost:5000/static/music/xxx.mp3
        
        # 让我们修改 SongService 让他接受 host_url 参数，或者在这里拼
        # 为了不改动太多，我们在 toDict 返回给前端前，手动拼一下
        
        data = newSong.toDict()
        # 简单的修正逻辑 (如果已经是 http 开头就不拼)
        if data['url'] and not data['url'].startswith('http'):
             data['url'] = f"{request.host_url}{data['url'].lstrip('/')}"
        if data['cover'] and not data['cover'].startswith('http'):
             data['cover'] = f"{request.host_url}{data['cover'].lstrip('/')}"

        return success(data=data, msg="Upload successful")
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return error(str(e), 500)