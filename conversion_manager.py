from services.file_detector import detect_file_type

def item(id,name,target,kind='conversion',**meta):
    d={'id':id,'name':name,'target':target,'kind':kind}; d.update(meta); return d

IMAGE=[
 item('png_to_jpg','PNG → JPG','jpg'), item('jpg_to_png','JPG → PNG','png'), item('image_to_webp','Image → WEBP','webp'),
 item('image_to_tiff','Image → TIF','tif'), item('image_to_bmp','Image → BMP','bmp'), item('gif_to_jpg','GIF → JPG','jpg'),
 item('gif_to_png','GIF → PNG','png'), item('tif_to_jpg','TIF → JPG','jpg'), item('bmp_to_jpg','BMP → JPG','jpg'),
 item('heic_to_jpg','HEIC → JPG','jpg'), item('images_to_pdf','Images → PDF','pdf'), item('images_to_word','Images → Word','docx'),
 item('gif_maker','GIF Maker','gif','tool')]

CONVERSION_MAP={
'image':{ext:IMAGE for ext in ('png','jpg','jpeg','webp','gif','bmp','tif','tiff','heic','heif')},
'pdf':{'pdf':[
 item('pdf_to_word','PDF → Word','docx'), item('pdf_to_excel','PDF → Excel','xlsx'), item('pdf_to_pptx','PDF → PPTX','pptx'),
 item('pdf_to_pages','PDF → Pages','docx'), item('pdf_to_numbers','PDF → Numbers','xlsx'), item('pdf_to_keynote','PDF → Keynote','pptx'),
 item('pdf_to_images','PDF → Images','jpg'), item('pdf_to_jpg','PDF → JPG','jpg'), item('pdf_to_png','PDF → PNG','png'), item('pdf_to_tif','PDF → TIF','tif'),
 item('pdf_to_epub','PDF → EPUB','epub'), item('pdf_to_mobi','PDF → MOBI','mobi'),
 item('merge_pdf','Merge PDF','pdf','tool'), item('split_pdf','Split PDF','pdf','tool'), item('rotate_pdf','Rotate PDF','pdf','tool'),
 item('compress_pdf','Compress PDF','pdf','tool'), item('unlock_pdf','Unlock PDF','pdf','tool'), item('encrypt_pdf','Encrypt PDF','pdf','tool'),
 item('watermark_pdf','PDF Watermark','pdf','tool'), item('page_numbers','Page Number','pdf','tool'), item('extract_images','Extract Images','zip','tool'),
 item('reorder_pages','Reorder Pages','pdf','tool'), item('delete_pages','Delete Pages','pdf','tool'), item('edit_pdf','PDF Studio','pdf','editor')]},
'word':{'docx':[item('docx_to_pdf','Word → PDF','pdf'),item('docx_to_txt','Word → TXT','txt'),item('docx_to_jpg','Word → JPG','jpg'),item('docx_to_png','Word → PNG','png'),item('edit_word','Word Studio','docx','editor')]},
'excel':{'xlsx':[item('xlsx_to_pdf','Excel → PDF','pdf'),item('xlsx_to_csv','Excel → CSV','csv')],'csv':[item('csv_to_xlsx','CSV → Excel','xlsx')]},
'powerpoint':{'pptx':[item('pptx_to_pdf','PPTX → PDF','pdf'),item('pptx_to_jpg','PPTX → JPG','jpg'),item('pptx_to_png','PPTX → PNG','png')]},
'text':{'txt':[item('txt_to_pdf','TXT → PDF','pdf'),item('txt_to_word','TXT → Word','docx')],'odt':[item('odt_to_pdf','ODT → PDF','pdf')],'html':[item('html_to_pdf','HTML → PDF','pdf')],'htm':[item('html_to_pdf','HTML → PDF','pdf')]},
'archive':{'zip':[item('zip_extract','Extract ZIP','folder','tool')]},'ebook':{'epub':[item('epub_to_pdf','EPUB → PDF','pdf'),item('epub_to_mobi','EPUB → MOBI','mobi')],'mobi':[item('mobi_to_pdf','MOBI → PDF','pdf')]}}

def get_available_conversions(filename):
    i=detect_file_type(filename); return CONVERSION_MAP.get(i.get('category'),{}).get(i.get('extension','').lstrip('.'),[])

def get_conversion_by_id(filename,cid):
    return next((x for x in get_available_conversions(filename) if x['id']==cid),None)
