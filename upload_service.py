import os,uuid
from werkzeug.utils import secure_filename
from config import Config
from services.file_detector import detect_file_type
from services.validation_service import validate_uploaded_file
FOLDERS={'image':'images','pdf':'pdf','word':'word','excel':'excel','powerpoint':'powerpoint','text':'text','archive':'archive'}
def save_uploaded_file(file):
    ok,e=validate_uploaded_file(file)
    if not ok:raise ValueError(e)
    info=detect_file_type(file.filename);safe=secure_filename(file.filename);stem,ext=os.path.splitext(safe);name=f'{stem}_{uuid.uuid4().hex[:24]}{ext.lower()}';folder=os.path.join(Config.UPLOAD_FOLDER,FOLDERS[info['category']]);os.makedirs(folder,exist_ok=True);path=os.path.join(folder,name);file.save(path)
    return {'original_filename':file.filename,'filename':name,'path':path,'extension':info['extension'],'category':info['category'],'type_name':info['name'],'size':os.path.getsize(path)}
