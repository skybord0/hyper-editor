import os
from config import Config
from services.file_detector import is_supported_file
MAX_FILE_SIZE=Config.MAX_CONTENT_LENGTH
def validate_filename(filename):
    if not filename or not filename.strip():return False,'No file was selected.'
    if not is_supported_file(filename):return False,'This file type is not supported by HYPER EDITOR.'
    return True,None
def validate_file_size(file):
    if file is None:return False,'No file was received.'
    try:pos=file.stream.tell();file.stream.seek(0,os.SEEK_END);size=file.stream.tell();file.stream.seek(pos)
    except Exception:return False,'Unable to determine the file size.'
    if size<=0:return False,'The selected file is empty.'
    if size>MAX_FILE_SIZE:return False,'File size exceeds the 250 MB limit.'
    return True,None
def validate_uploaded_file(file):
    if file is None:return False,'No file was received.'
    ok,e=validate_filename(file.filename)
    if not ok:return ok,e
    return validate_file_size(file)
