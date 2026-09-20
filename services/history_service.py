import os,json,threading
from datetime import datetime
from config import Config
PATH=os.path.join(Config.INSTANCE_FOLDER,'history.json');LOCK=threading.Lock()
def get_history():
    try:
        with open(PATH,encoding='utf8') as f:return json.load(f)
    except Exception:return []
def add_history(original,operation,output=None,status='success'):
    os.makedirs(Config.INSTANCE_FOLDER,exist_ok=True)
    with LOCK:
        items=get_history();items.insert(0,{'time':datetime.now().isoformat(timespec='seconds'),'original':original,'operation':operation,'output':output,'status':status});items[:]=items[:200]
        with open(PATH,'w',encoding='utf8') as f:json.dump(items,f,indent=2)
def clear_history():
    os.makedirs(Config.INSTANCE_FOLDER,exist_ok=True)
    with open(PATH,'w',encoding='utf8') as f:json.dump([],f)
