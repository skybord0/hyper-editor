import os,uuid,shutil
from flask import Blueprint,jsonify,request,render_template,send_file
import pymupdf
from config import Config
from services.pdf_editor_service import session_dir,load_state,create_session,doc,page_info,spans,words,replace_span,add_text,annotate,redact,shape,freehand,insert_image,page_op,undo,redo
from services.ocr_service import ocr_page
pdf_editor_bp=Blueprint('pdf_editor',__name__)

def find_pdf(name):
    p=os.path.join(Config.UPLOAD_FOLDER,'pdf',os.path.basename(name)); return p if os.path.isfile(p) else None
@pdf_editor_bp.get('/pdf-editor')
def page():return render_template('pdf_editor/editor.html')
@pdf_editor_bp.post('/api/pdf-editor/open')
def open_editor():
    data=request.get_json(silent=True) or {}; name=os.path.basename(data.get('filename','')); src=find_pdf(name)
    if not src:return jsonify({'success':False,'error':'PDF not found.'}),404
    st=create_session(src,name); d=doc(st['id']); info=page_info(d); d.close(); return jsonify({'success':True,'session_id':st['id'],'filename':name,'pages':info})
@pdf_editor_bp.get('/api/pdf-editor/<sid>/page/<int:page>/image')
def image(sid,page):
    d=doc(sid)
    if page<0 or page>=d.page_count:d.close();return jsonify({'error':'Page not found'}),404
    p=os.path.join(session_dir(sid),f'render_{page}_{uuid.uuid4().hex}.png'); d[page].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),alpha=False).save(p); d.close(); return send_file(p,mimetype='image/png',max_age=0)
@pdf_editor_bp.get('/api/pdf-editor/<sid>/page/<int:page>/text')
def text(sid,page):
    d=doc(sid)
    if page<0 or page>=d.page_count:d.close();return jsonify({'success':False,'error':'Page not found'}),404
    out=spans(d[page]); wd=words(d[page]); rect=d[page].rect; d.close(); return jsonify({'success':True,'spans':out,'words':wd,'page':{'width':rect.width,'height':rect.height}})
@pdf_editor_bp.post('/api/pdf-editor/<sid>/operation')
def operation(sid):
    x=request.get_json(silent=True) or {}; op=x.get('operation')
    try:
        if op=='replace_span':replace_span(sid,int(x['page']),x['bbox'],x.get('text',''),x.get('size',11),x.get('color',0),x.get('font','helv'),x.get('font_xref'))
        elif op=='add_text':add_text(sid,int(x['page']),x['bbox'],x.get('text','Text'),x.get('size',14),x.get('color',[.1,.15,.25]))
        elif op in ('highlight','underline','strikeout'):annotate(sid,int(x['page']),x['bbox'],op,x.get('color',[1,.75,.05]))
        elif op=='redact':redact(sid,int(x['page']),x['bbox'])
        elif op in ('rectangle','ellipse','line'):shape(sid,int(x['page']),op,x['bbox'],x.get('color',[.12,.35,.9]),x.get('fill'),x.get('width',2))
        elif op=='freehand':freehand(sid,int(x['page']),x.get('points',[]),x.get('color',[.1,.2,.8]),x.get('width',2))
        elif op in ('rotate','delete','duplicate','add_blank'):page_op(sid,op,pages=x.get('pages',[]),degrees=int(x.get('degrees',90)),page=int(x.get('page',0)),after=int(x.get('after',0)))
        elif op=='reorder':page_op(sid,op,order=list(map(int,x.get('order',[]))))
        elif op=='undo':undo(sid)
        elif op=='redo':redo(sid)
        else:raise ValueError('Unsupported editor operation.')
        d=doc(sid); info=page_info(d); d.close(); return jsonify({'success':True,'pages':info})
    except Exception as e:return jsonify({'success':False,'error':str(e)}),400
@pdf_editor_bp.post('/api/pdf-editor/<sid>/insert-image')
def insert_img(sid):
    f=request.files.get('image')
    if not f:return jsonify({'success':False,'error':'Image not supplied.'}),400
    page=int(request.form.get('page','0')); bbox=[float(x) for x in request.form.get('bbox','80,80,330,280').split(',')]; path=os.path.join(session_dir(sid),uuid.uuid4().hex+os.path.splitext(f.filename)[1]); f.save(path)
    try:insert_image(sid,page,bbox,path); return jsonify({'success':True})
    finally:
        try:os.remove(path)
        except:pass

@pdf_editor_bp.post('/api/pdf-editor/<sid>/ocr/<int:page>')
def ocr(sid,page):
    try:
        d=doc(sid);
        if page<0 or page>=d.page_count: d.close(); return jsonify({'success':False,'error':'Page not found.'}),404
        text=ocr_page(d[page]); d.close(); return jsonify({'success':True,'text':text})
    except Exception as e:return jsonify({'success':False,'error':str(e)}),400

@pdf_editor_bp.post('/api/pdf-editor/<sid>/save')
def save(sid):
    st=load_state(sid); outdir=os.path.join(Config.OUTPUT_FOLDER,'pdf');os.makedirs(outdir,exist_ok=True);name=f"edited_{os.path.splitext(st['original_name'])[0]}_{uuid.uuid4().hex[:10]}.pdf";shutil.copy2(st['current'],os.path.join(outdir,name));return jsonify({'success':True,'file':{'filename':name,'download_url':f'/api/download/pdf/{name}'}})
