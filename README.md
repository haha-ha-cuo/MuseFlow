# MuseFlow - 简易音乐播放器

MuseFlow 是一个基于 Flask (后端) 和 Vue 3 (前端) 构建的简易音乐播放器项目。支持上传音乐、播放列表管理和音乐播放功能。

## 🚀 技术栈

- **后端**: Flask, SQLAlchemy (SQLite), Flask-CORS
- **前端**: Vue 3, Vite, Pinia, Vue Router, Lucide Vue Next
- **数据库**: SQLite

## 📂 项目结构

```
MuseFlow/
├── instance/          # SQLite 数据库文件 (music.db)
├── python/            # 后端代码
│   ├── model/         # 数据模型 (Song, SongList)
│   ├── static/        # 静态资源 (上传的音乐文件)
│   ├── test.py        # Flask 应用入口
│   └── extension.py   # 数据库扩展初始化
├── vue-project/       # 前端代码 (Vue 3 + Vite)
├── package.json       # 项目根目录配置 (包含并发运行脚本)
└── README.md          # 项目说明文档
```

## 🛠️ 安装与配置

### 1. 后端环境配置

确保已安装 Python 3.8+ 以及全局 uv。

```bash
# 使用 uv 同步环境
uv sync
```

### 2. 前端环境配置

确保已安装 Node.js (建议 v18+)。

```bash
cd vue-project
npm install
```

## ▶️ 运行项目

项目根目录提供了一个便捷的启动脚本，可以同时启动后端和前端服务。

```bash
# 在项目根目录下运行
npm install
npm run dev
```

该命令会执行：

1. 启动 Flask 后端服务 (默认端口 5000)
2. 启动 Vite 前端开发服务器

访问前端页面通常在 `http://localhost:5173`。

## ✨ 功能特性

- **音乐上传**: 支持上传 MP3/FLAC 等格式音乐文件。
- **播放列表**: 查看和管理播放列表。
- **音乐播放**: 网页端直接播放上传的音乐。
- **持久化存储**: 使用 SQLite 保存音乐元数据。

## 📝 注意事项

- 上传的音乐文件会保存在 `python/static/music` 目录下。
- 数据库文件位于 `instance/music.db`。
- 如果遇到跨域问题，请确保后端 `CORS` 配置正确。

## 📄 许可证

[MIT License](https://opensource.org/licenses/MIT)
