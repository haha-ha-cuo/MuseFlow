import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'music.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'music')
    COVER_FOLDER = os.path.join(basedir, 'static', 'cover')
    
    # 其他配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'

    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.COVER_FOLDER, exist_ok=True)