import os
import uuid
from flask import Flask, jsonify, request, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from model.Song import Song
from tinytag import TinyTag
from model.SongList import Playlist
from extension import db

# 1. 创建 Flask 应用实例
# static_folder='static' 告诉 Flask 静态文件存在哪里
app = Flask(__name__, static_folder='static', static_url_path='/static')


#注册数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# 配置上传保存路径
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'music')
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # 自动创建目录
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# 2. 启用 CORS (跨域资源共享)
# 这允许前端(Vue)跨域访问后端API
CORS(app, resources={r"/*": {"origins": "*"}})

# --- 新增功能：上传音乐 ---
@app.route('/api/upload/playlistId=<int:playlistId>', methods=['POST'])
def upload_file(playlistId):
    try:
        playlist = db.session.get(Playlist, playlistId)
    except Exception as e:
        return jsonify({"code": 500, "msg": "数据库查询错误", "error": str(e)}), 500
    
    if 'file' not in request.files:
        return jsonify({"code": 400, "msg": "没有上传文件"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"code": 400, "msg": "文件名为空"}), 400

    if file:
        # 获取文件扩展名
        ext = os.path.splitext(file.filename)[1]
        if not ext:
            ext = '.mp3' # 默认扩展名
            
        # 使用 UUID 生成唯一文件名，防止中文名乱码和文件覆盖
        filename = f"{uuid.uuid4().hex}{ext}"

        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        # 生成可访问的 URL
        # request.host_url 是 http://127.0.0.1:5000/
        file_url = f"{request.host_url}static/music/{filename}"

        # 从文件中提取元数据
        duration = None
        artist = "Unknown Artist"
        try:
            # 显式创建 TinyTag 对象，并在使用后尝试清理
            # TinyTag.get() 实际上返回一个新的 TinyTag 实例，并在内部打开文件
            # 我们手动删除引用来提示 GC
            tag = TinyTag.get(save_path)
            if tag:
                duration = int(tag.duration) if tag.duration else None
                artist = tag.artist if tag.artist else "Unknown Artist"
                
                # 显式删除引用，虽然 Python 是自动 GC，但在 Windows 上这可能有助于快速释放句柄
                del tag
        except Exception as e:
            print(f"元数据提取警告: {e}") # 不阻断上传流程，只打印警告
        
        # 把新歌加到我们的数据库里
        newSong = Song(
            title=request.form.get('name', 'Unknown Title'),
            artist=artist,
            cover="https://placehold.co/300x300?text=Music",
            url=file_url,
            source=filename,
            duration=duration
        )

        playlist.songs.append(newSong)
        db.session.commit()

        print(f"上传成功: {newSong.toDict()}")

        return jsonify({
            "code": 200,
            "msg": "上传成功",
            "data": newSong.toDict()
        })

# --- 新增功能：获取所有歌单 ---
@app.route('/api/playlists', methods=['GET'])
def getPlaylists():
    """
    获取推荐歌单列表
    """
    # 从数据库获取所有歌单
    playlists = Playlist.query.all()
    
    # 如果数据库为空，创建一个默认歌单
    if not playlists:
        default_playlist = Playlist(
            title="My Playlist",
            artist="Apple Music",
            cover="https://is1-ssl.mzstatic.com/image/thumb/Features122/v4/71/3b/38/713b381e-1285-d602-0c9f-39589f816c7f/source/600x600bb.jpg",
            description="Songs from your server."
        )
        db.session.add(default_playlist)
        db.session.commit()
        playlists = [default_playlist]
    
    return jsonify({
        "code": 200,
        "msg": "success",
        "data": [p.toDict() for p in playlists]
    })

@app.route('/api/playlists/upload', methods=['POST'])
def upload_playlist():
    """
    上传新歌单
    """
    data = request.json
    if not data or 'title' not in data or 'artist' not in data:
        return jsonify({"code": 400, "msg": "缺少必要字段"}), 400
    
    new_playlist = Playlist(
        title=data['title'],
        artist=data['artist'],
        cover=data.get('cover'), # 默认为 None，前端会显示自动生成的占位符
        description=data.get('description', "Songs from your server.")
    )
    db.session.add(new_playlist)
    db.session.commit()
    
    return jsonify({
        "code": 200,
        "msg": "歌单上传成功",
        "data": new_playlist.toDict()
    })

@app.route('/api/playlists/id=<int:id>', methods=['GET'])
def getSongs(id):
     """
     获取所有歌曲列表
     """
    
     playlist = db.session.get(Playlist, id)
     if not playlist:
        return jsonify({"code": 404, "msg": "歌单不存在"}), 404
     
     # 将查询结果转换为字典列表
     songList = [song.toDict() for song in playlist.songs]
    
     return jsonify({
         "code": 200,
         "msg": "success",
         "title": playlist.title,
         "description": playlist.description,
         "data": songList
     })

@app.route('/api/songs/<int:id>', methods=['DELETE'])
def delete_song(id):
    try:
        song = db.session.get(Song, id)
        if not song:
            return jsonify({"code": 404, "msg": "歌曲不存在"}), 404

        # 1. 获取文件路径
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], song.source)
        
        # 2. 先删数据库 (Commit)
        db.session.delete(song)
        db.session.commit()
        
        # 3. 再尝试删文件 (允许失败)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as file_error:
                print(f"Warning: 文件删除失败 {file_path}: {file_error}")
    
        return jsonify({"code": 200, "msg": "删除成功"})
        
    except Exception as e:
        db.session.rollback()
        print(f"Delete Error: {e}")
        return jsonify({"code": 500, "msg": str(e)}), 500

@app.route('/api/songs/update/<int:id>',methods = ['PUT'])
def update_song(id):
    """
    更新歌曲信息
    """
    data = request.json
    if not data or 'title' not in data or 'artist' not in data:
        return jsonify({"code": 400, "msg": "缺少必要字段"}), 400
    
    song = db.session.get(Song, id)
    if not song:
        return jsonify({"code": 404, "msg": "歌曲不存在"}), 404
    
    song.title = data['title']
    song.artist = data['artist']
    song.cover = data.get('cover') # 默认为 None，前端会显示自动生成的占位符
    db.session.commit()
    
    return jsonify({
        "code": 200,
        "msg": "歌曲更新成功",
        "data": song.toDict()
    })

@app.route('/api/playlists/update/<int:id>',methods = ['PUT'])
def update_playlist(id):
    """
    更新歌单信息
    """
    data = request.json
    if not data or 'title' not in data or 'description' not in data:
        return jsonify({"code": 400, "msg": "缺少必要字段"}), 400
    
    playlist = db.session.get(Playlist, id)
    if not playlist:
        return jsonify({"code": 404, "msg": "歌单不存在"}), 404
    
    playlist.title = data['title']
    playlist.description = data['description']
    playlist.cover = data.get('cover') # 默认为 None，前端会显示自动生成的占位符
    db.session.commit()
    
    return jsonify({
        "code": 200,
        "msg": "歌单更新成功",
        "data": playlist.toDict()
    })
# 4. 启动应用
if __name__ == '__main__':
    # debug=True 表示开启调试模式，代码修改后会自动重启
    # port=5000 指定运行端口
    app.run(debug=True, port=5000)
