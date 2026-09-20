import os
CATEGORY_MAP={
'png':('image','PNG'),'jpg':('image','JPG'),'jpeg':('image','JPEG'),'webp':('image','WEBP'),'gif':('image','GIF'),'bmp':('image','BMP'),'tif':('image','TIFF'),'tiff':('image','TIFF'),'heic':('image','HEIC'),'heif':('image','HEIF'),
'pdf':('pdf','PDF'),'docx':('word','Word'),'xlsx':('excel','Excel'),'csv':('excel','CSV'),'pptx':('powerpoint','PowerPoint'),'txt':('text','Text'),'odt':('text','ODT'),'epub':('ebook','EPUB'),'mobi':('ebook','MOBI'),'html':('text','HTML'),'htm':('text','HTML'),'zip':('archive','ZIP')}
def detect_file_type(filename):
    ext=os.path.splitext(os.path.basename(filename or ''))[1].lower().lstrip('.')
    v=CATEGORY_MAP.get(ext)
    return {'detected':bool(v),'category':v[0] if v else None,'extension':f'.{ext}' if ext else '','filename':os.path.basename(filename or ''),'name':v[1] if v else None}
def is_supported_file(filename): return detect_file_type(filename)['detected']
