import os
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
class Config:
    SECRET_KEY=os.environ.get('SECRET_KEY','hyper-editor-change-me')
    MAX_CONTENT_LENGTH=250*1024*1024
    UPLOAD_FOLDER=os.path.join(BASE_DIR,'uploads')
    OUTPUT_FOLDER=os.path.join(BASE_DIR,'outputs')
    LOG_FOLDER=os.path.join(BASE_DIR,'logs')
    INSTANCE_FOLDER=os.path.join(BASE_DIR,'instance')
    EDITOR_FOLDER=os.path.join(BASE_DIR,'instance','editor_sessions')
    ALLOWED_EXTENSIONS={'png','jpg','jpeg','webp','gif','bmp','tif','tiff','pdf','docx','xlsx','csv','pptx','txt','html','htm','zip','heic','heif','odt','epub','mobi'}
