import os,uuid
from flask import Blueprint,jsonify,request,render_template
from config import Config
from services.word_editor_service import extract_docx,save_docx
word_editor_bp=Blueprint('word_editor',__name__)
def find(name):
 p=os.path.join(Config.UPLOAD_FOLDER,'word',os.path.basename(name));return p if os.path.isfile(p) else None
@word_editor_bp.get('/word-editor')
def page():return render_template('word_editor.html')
@word_editor_bp.post('/api/word-editor/open')
def open_word():
 d=request.get_json(silent=True) or {};name=os.path.basename(d.get('filename',''));p=find(name)
 if not p:return jsonify({'success':False,'error':'Word file not found.'}),404
 return jsonify({'success':True,'filename':name,'document':extract_docx(p)})
@word_editor_bp.post('/api/word-editor/save')
def save_word():
 d=request.get_json(silent=True) or {};name=os.path.basename(d.get('filename',''));p=find(name)
 if not p:return jsonify({'success':False,'error':'Word file not found.'}),404
 outdir=os.path.join(Config.OUTPUT_FOLDER,'word');os.makedirs(outdir,exist_ok=True);out=f'edited_{os.path.splitext(name)[0]}_{uuid.uuid4().hex[:10]}.docx';save_docx(os.path.join(outdir,out),d.get('document',{}));return jsonify({'success':True,'file':{'filename':out,'download_url':f'/api/download/word/{out}'}})
