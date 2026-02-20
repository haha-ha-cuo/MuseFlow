import os
from flask import Flask, jsonify, request, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
import random
from model.Song import Song
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

# --- 模拟数据库数据 ---
# 在真实项目中，这些数据会存储在 MySQL 或 SQLite 数据库中
MOCK_PLAYLISTS = [
    {
        "id": 1,
        "title": "My Playlist",
        "artist": "Apple Music",
        "cover": "https://is1-ssl.mzstatic.com/image/thumb/Features122/v4/71/3b/38/713b381e-1285-d602-0c9f-39589f816c7f/source/600x600bb.jpg"
    },
]

# 2. 启用 CORS (跨域资源共享)
# 这允许前端(Vue)跨域访问后端API
CORS(app, resources={r"/*": {"origins": "*"}})

# --- 新增功能：上传音乐 ---
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"code": 400, "msg": "没有上传文件"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"code": 400, "msg": "文件名为空"}), 400

    if file:
        # 安全处理文件名 (比如把 "我的 歌.mp3" 变成 "My_Song.mp3")
        # 注意：secure_filename 可能会把中文名变空，生产环境建议用 uuid 重命名
        filename = secure_filename(file.filename)
        if not filename:
             # 简单的回退策略：如果是纯中文导致为空，就用时间戳
             import time
             filename = f"music_{int(time.time())}.mp3"

        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        # 生成可访问的 URL
        # request.host_url 是 http://127.0.0.1:5000/
        file_url = f"{request.host_url}static/music/{filename}"

        # 把新歌加到我们的数据库里
        newSong = Song(
            title=request.form.get('name', 'Unknown Title'),
            artist="Unknown Artist",
            cover="https://placehold.co/300x300?text=Music",
            url=file_url,
            source=filename
        )
        db.session.add(newSong)
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
    # 可以在这里添加业务逻辑，比如只返回前10个，或者根据用户喜好排序
    
    
    return jsonify({
        "code": 200,
        "msg": "success",
        "data": MOCK_PLAYLISTS
    })

@app.route('/api/playlists/id=<int:id>', methods=['GET'])
def getSongs(id):
     """
     获取所有歌曲列表
     """
     # 查询数据库获取所有歌曲
     songs = Song.query.all()
     
     # 将查询结果转换为字典列表
     songList = [song.toDict() for song in songs]
    
     return jsonify({
         "code": 200,
         "msg": "success",
         "data": songList
     })

@app.route('/api/songs/<int:id>', methods=['DELETE'])
def delete_song(id):
    try:
        song = Song.query.get(id)
        if song:
            db.session.delete(song)
            db.session.commit()
            
            # 删除文件
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], song.source)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return jsonify({"code": 200, "msg": "删除成功"})
        return jsonify({"code": 404, "msg": "歌曲不存在"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": str(e)}), 500


# 4. 启动应用
if __name__ == '__main__':
    # debug=True 表示开启调试模式，代码修改后会自动重启
    # port=5000 指定运行端口
    app.run(debug=True, port=5000)
