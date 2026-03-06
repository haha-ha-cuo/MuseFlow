import os
from flask import Flask
from flask_cors import CORS
from extension import db
from flask_migrate import Migrate
from api import playlists_bp, songs_bp, upload_bp
from config import Config

# 1. 创建 Flask 应用实例
# static_folder='static' 告诉 Flask 静态文件存在哪里
app = Flask(__name__, static_folder='static', static_url_path='/static')

# 加载配置
app.config.from_object(Config)
Config.init_app(app)

# 初始化扩展
db.init_app(app)
migrate = Migrate(app, db)

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
