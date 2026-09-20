from flask import Blueprint,jsonify,request
from services.upload_service import save_uploaded_file
upload_bp=Blueprint('upload',__name__,url_prefix='/api')
@upload_bp.post('/upload')
def upload():
    try:return jsonify({'success':True,'file':save_uploaded_file(request.files.get('file'))})
    except ValueError as e:return jsonify({'success':False,'error':str(e)}),400
    except Exception:return jsonify({'success':False,'error':'Unable to upload the file.'}),500
