import os
from flask import Flask
from flask_cors import CORS
from extension import db
from flask_migrate import Migrate
from api import playlists_bp, songs_bp, upload_bp

# 1. 创建 Flask 应用实例
# static_folder='static' 告诉 Flask 静态文件存在哪里
app = Flask(__name__, static_folder='static', static_url_path='/static')


#注册数据库
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'music.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)


# 配置上传保存路径
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'music')
COVER_FOLDER = os.path.join(app.root_path, 'static', 'cover')
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # 自动创建目录
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(COVER_FOLDER, exist_ok=True) # 自动创建目录
app.config['COVER_FOLDER'] = COVER_FOLDER


# 2. 启用 CORS (跨域资源共享)
# 这允许前端(Vue)跨域访问后端API
CORS(app, resources={r"/*": {"origins": "*"}})

# 注册蓝图
app.register_blueprint(playlists_bp, url_prefix='/api/playlists')
app.register_blueprint(songs_bp, url_prefix='/api/songs')
app.register_blueprint(upload_bp, url_prefix='/api/upload')

# 4. 启动应用
if __name__ == '__main__':
    # debug=True 表示开启调试模式，代码修改后会自动重启
    # port=5000 指定运行端口
    app.run(debug=True, port=5000)
