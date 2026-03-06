import os
import uuid
from flask import current_app

class FileService:
    @staticmethod
    def save_file(file, folder_config_key, default_ext='.mp3'):
        """
        保存文件到指定目录
        :param file: FileStorage 对象
        :param folder_config_key: app.config 中的键名 (e.g., 'UPLOAD_FOLDER')
        :param default_ext: 默认扩展名
        :return: (filename, full_path, file_url)
        """
        if not file:
            return None, None, None
            
        ext = os.path.splitext(file.filename)[1]
        if not ext:
            ext = default_ext
            
        filename = f"{uuid.uuid4().hex}{ext}"
        folder = current_app.config[folder_config_key]
        path = os.path.join(folder, filename)
        
        file.save(path)
        
        # 构建 URL (假设静态资源映射规则是固定的)
        # TODO: 这里 URL 构造逻辑可能需要根据 folder_config_key 动态调整
        # 目前 music -> /static/music, cover -> /static/cover
        url_prefix = '/static/music' if 'UPLOAD' in folder_config_key else '/static/cover'
        # 这里的 host_url 需要在 controller 层处理或者这里传进来，或者只返回相对路径
        # 为了解耦，这里返回相对路径
        relative_url = f"{url_prefix}/{filename}"
        
        return filename, path, relative_url

    @staticmethod
    def delete_file(filename, folder_config_key):
        if not filename: return
        
        folder = current_app.config[folder_config_key]
        path = os.path.join(folder, filename)
        
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Warning: Failed to delete file {path}: {e}")