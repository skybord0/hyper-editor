import os
from flask import Blueprint,send_from_directory,abort
from config import Config
download_bp=Blueprint('download',__name__,url_prefix='/api/download')
MAP={'images':'images','pdf':'pdf','word':'word','excel':'excel','powerpoint':'powerpoint','text':'text','archive':'archive'}
@download_bp.get('/<category>/<path:filename>')
def download(category,filename):
    if category not in MAP:abort(404)
    return send_from_directory(os.path.join(Config.OUTPUT_FOLDER,MAP[category]),filename,as_attachment=True)
