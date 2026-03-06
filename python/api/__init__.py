from flask import Blueprint

playlists_bp = Blueprint('playlists', __name__)
songs_bp = Blueprint('songs', __name__)
upload_bp = Blueprint('upload', __name__)

from . import playlists, songs, upload