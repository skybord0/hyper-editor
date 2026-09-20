import os, uuid, zipfile, shutil, subprocess
from flask import Blueprint, jsonify, request
import pymupdf
from config import Config
from services.conversion_manager import get_available_conversions, get_conversion_by_id
from services.history_service import add_history
from utils.naming_utils import output_name
from converters.image.png_to_jpg import convert_png_to_jpg
from converters.image.jpg_to_png import convert_jpg_to_png
from converters.image.image_to_webp import convert_image_to_webp
from converters.image.images_to_pdf import convert_images_to_pdf
from converters.image.images_to_word import convert_images_to_word
from converters.image.image_to_tiff import convert_image_to_tiff
from converters.image.image_to_bmp import convert_image_to_bmp
from converters.image.image_to_gif import make_gif
from converters.image.heic_to_jpg import convert_heic_to_jpg
from converters.image.tif_to_jpg import convert_tif_to_jpg
from converters.image.bmp_to_jpg import convert_bmp_to_jpg
from converters.image.gif_to_jpg import convert_gif_to_jpg
from converters.image.gif_to_png import convert_gif_to_png
from converters.pdf.pdf_to_jpg import convert_pdf_to_jpg
from converters.pdf.pdf_to_png import convert_pdf_to_png
from converters.pdf.pdf_to_tif import convert_pdf_to_tif
from converters.pdf.pdf_to_txt import convert_pdf_to_txt
from converters.pdf.pdf_to_word import convert_pdf_to_word
from converters.pdf.pdf_to_excel import convert_pdf_to_excel
from converters.pdf.pdf_to_pptx import convert_pdf_to_pptx
from converters.pdf.pdf_to_pages import pdf_to_pages_zip
from converters.pdf.ebook_converters import pdf_to_epub,pdf_to_mobi
from converters.pdf.merge_pdf import merge_pdf_files
from converters.pdf.split_pdf import split_pdf
from converters.pdf.compress_pdf import compress_pdf
from converters.word.docx_to_txt import convert_docx_to_txt
from converters.word.docx_to_pdf import convert_docx_to_pdf
from converters.word.docx_to_jpg import convert_docx_to_jpg
from converters.word.docx_to_png import convert_docx_to_png
from converters.excel.xlsx_to_csv import convert_xlsx_to_csv
from converters.excel.csv_to_xlsx import convert_csv_to_xlsx
from converters.excel.xlsx_to_pdf import convert_xlsx_to_pdf
from converters.powerpoint.pptx_to_pdf import convert_pptx_to_pdf
from converters.powerpoint.pptx_to_jpg import convert_pptx_to_jpg
from converters.powerpoint.pptx_to_png import convert_pptx_to_png
from converters.text.txt_to_pdf import txt_to_pdf
from converters.text.txt_to_word import txt_to_word
from converters.text.html_to_pdf import html_to_pdf
from converters.text.odt_to_pdf import odt_to_pdf
from converters.text.ebook_to_pdf import ebook_to_pdf,epub_to_mobi,mobi_to_pdf
from converters.archive.zip_extract import extract_zip

conversion_bp=Blueprint('conversion',__name__,url_prefix='/api')
FOLDERS={'image':'images','pdf':'pdf','word':'word','excel':'excel','powerpoint':'powerpoint','text':'text','archive':'archive'}

def folder(category):
    p=os.path.join(Config.OUTPUT_FOLDER,FOLDERS[category]); os.makedirs(p,exist_ok=True); return p

def uploaded(filename):
    name=os.path.basename(filename or '')
    for f in FOLDERS.values():
        p=os.path.join(Config.UPLOAD_FOLDER,f,name)
        if os.path.isfile(p): return p
    return None

def file_result(category,name,cid=None,files=None):
    r={'success':True,'file':{'filename':name,'download_url':f'/api/download/{FOLDERS[category]}/{name}'}}
    if cid:r['file']['conversion_id']=cid
    if files:r['files']=[{'filename':x,'download_url':f'/api/download/{FOLDERS[category]}/{x}'} for x in files]
    return r

def multi_result(category,files,cid):
    return {'success':True,'file':{'filename':files[0],'download_url':f'/api/download/{FOLDERS[category]}/{files[0]}','conversion_id':cid},'files':[{'filename':x,'download_url':f'/api/download/{FOLDERS[category]}/{x}'} for x in files]}

@conversion_bp.get('/conversions')
def conversions():
    name=request.args.get('filename','').strip()
    if not name:return jsonify({'success':False,'error':'Filename was not provided.'}),400
    return jsonify({'success':True,'filename':name,'conversions':get_available_conversions(name)})

@conversion_bp.post('/convert')
def convert():
    d=request.get_json(silent=True) or {}; name=str(d.get('filename','')).strip(); cid=str(d.get('conversion_id','')).strip(); src=uploaded(name)
    if not src:return jsonify({'success':False,'error':'Uploaded file was not found.'}),404
    if not get_conversion_by_id(name,cid):return jsonify({'success':False,'error':'This conversion is not available for the selected file.'}),400
    try:
        if cid in ('edit_pdf','edit_word'):
            return jsonify({'success':True,'editor_url':('/pdf-editor?filename=' if cid=='edit_pdf' else '/word-editor?filename=')+name})
        if cid=='png_to_jpg': out=output_name(name,'jpg'); convert_png_to_jpg(src,os.path.join(folder('image'),out)); res=file_result('image',out,cid)
        elif cid=='jpg_to_png': out=output_name(name,'png'); convert_jpg_to_png(src,os.path.join(folder('image'),out)); res=file_result('image',out,cid)
        elif cid=='image_to_webp': out=output_name(name,'webp'); convert_image_to_webp(src,os.path.join(folder('image'),out)); res=file_result('image',out,cid)
        elif cid=='image_to_tiff': out=output_name(name,'tif'); convert_image_to_tiff(src,os.path.join(folder('image'),out)); res=file_result('image',out,cid)
        elif cid=='image_to_bmp': out=output_name(name,'bmp'); convert_image_to_bmp(src,os.path.join(folder('image'),out)); res=file_result('image',out,cid)
        elif cid=='tif_to_jpg': out=output_name(name,'jpg'); convert_tif_to_jpg(src,os.path.join(folder('image'),out)); res=file_result('image',out,cid)
        elif cid=='bmp_to_jpg': out=output_name(name,'jpg'); convert_bmp_to_jpg(src,os.path.join(folder('image'),out)); res=file_result('image',out,cid)
        elif cid=='gif_to_jpg': out=output_name(name,'jpg'); convert_gif_to_jpg(src,os.path.join(folder('image'),out)); res=file_result('image',out,cid)
        elif cid=='gif_to_png': out=output_name(name,'png'); convert_gif_to_png(src,os.path.join(folder('image'),out)); res=file_result('image',out,cid)
        elif cid=='heic_to_jpg': out=output_name(name,'jpg'); convert_heic_to_jpg(src,os.path.join(folder('image'),out)); res=file_result('image',out,cid)
        elif cid in ('images_to_pdf','images_to_word'):
            out=output_name(name,'pdf' if cid=='images_to_pdf' else 'docx'); cat='pdf' if cid=='images_to_pdf' else 'word'; fn=convert_images_to_pdf if cid=='images_to_pdf' else convert_images_to_word; fn([src],os.path.join(folder(cat),out)); res=file_result(cat,out,cid)
        elif cid=='pdf_to_jpg': res=multi_result('image',convert_pdf_to_jpg(src,folder('image')),cid)
        elif cid=='pdf_to_png': res=multi_result('image',convert_pdf_to_png(src,folder('image')),cid)
        elif cid=='pdf_to_tif': res=multi_result('image',convert_pdf_to_tif(src,folder('image')),cid)
        elif cid=='pdf_to_images': res=multi_result('image',convert_pdf_to_jpg(src,folder('image')),cid)
        elif cid=='pdf_to_txt': out=output_name(name,'txt'); convert_pdf_to_txt(src,os.path.join(folder('text'),out)); res=file_result('text',out,cid)
        elif cid=='pdf_to_word': out=output_name(name,'docx'); convert_pdf_to_word(src,os.path.join(folder('word'),out)); res=file_result('word',out,cid)
        elif cid in ('pdf_to_excel','pdf_to_numbers'): out=output_name(name,'xlsx'); convert_pdf_to_excel(src,os.path.join(folder('excel'),out)); res=file_result('excel',out,cid)
        elif cid in ('pdf_to_pptx','pdf_to_keynote'): out=output_name(name,'pptx'); convert_pdf_to_pptx(src,os.path.join(folder('powerpoint'),out)); res=file_result('powerpoint',out,cid); res['note']='Keynote-compatible PPTX. Native .key generation requires Apple Keynote/macOS.' if cid=='pdf_to_keynote' else None
        elif cid=='pdf_to_pages': out=output_name(name,'docx'); convert_pdf_to_word(src,os.path.join(folder('word'),out)); res=file_result('word',out,cid); res['note']='Pages-compatible DOCX. Native .pages generation requires Apple Pages/macOS.'
        elif cid=='pdf_to_epub': out=output_name(name,'epub'); pdf_to_epub(src,os.path.join(folder('archive'),out)); res=file_result('archive',out,cid)
        elif cid=='pdf_to_mobi': out=output_name(name,'mobi'); pdf_to_mobi(src,os.path.join(folder('archive'),out)); res=file_result('archive',out,cid)
        elif cid=='docx_to_txt': out=output_name(name,'txt'); convert_docx_to_txt(src,os.path.join(folder('text'),out)); res=file_result('text',out,cid)
        elif cid=='docx_to_pdf': out=output_name(name,'pdf'); convert_docx_to_pdf(src,os.path.join(folder('pdf'),out)); res=file_result('pdf',out,cid)
        elif cid=='docx_to_jpg': res=multi_result('image',convert_docx_to_jpg(src,folder('image')),cid)
        elif cid=='docx_to_png': res=multi_result('image',convert_docx_to_png(src,folder('image')),cid)
        elif cid=='xlsx_to_csv': out=output_name(name,'csv'); convert_xlsx_to_csv(src,os.path.join(folder('excel'),out)); res=file_result('excel',out,cid)
        elif cid=='csv_to_xlsx': out=output_name(name,'xlsx'); convert_csv_to_xlsx(src,os.path.join(folder('excel'),out)); res=file_result('excel',out,cid)
        elif cid=='xlsx_to_pdf': out=output_name(name,'pdf'); convert_xlsx_to_pdf(src,os.path.join(folder('pdf'),out)); res=file_result('pdf',out,cid)
        elif cid=='pptx_to_pdf': out=output_name(name,'pdf'); convert_pptx_to_pdf(src,os.path.join(folder('pdf'),out)); res=file_result('pdf',out,cid)
        elif cid=='pptx_to_jpg': res=multi_result('image',convert_pptx_to_jpg(src,folder('image')),cid)
        elif cid=='pptx_to_png': res=multi_result('image',convert_pptx_to_png(src,folder('image')),cid)
        elif cid=='txt_to_pdf': out=output_name(name,'pdf'); txt_to_pdf(src,os.path.join(folder('pdf'),out)); res=file_result('pdf',out,cid)
        elif cid=='txt_to_word': out=output_name(name,'docx'); txt_to_word(src,os.path.join(folder('word'),out)); res=file_result('word',out,cid)
        elif cid=='html_to_pdf': out=output_name(name,'pdf'); html_to_pdf(src,os.path.join(folder('pdf'),out)); res=file_result('pdf',out,cid)
        elif cid=='odt_to_pdf': out=output_name(name,'pdf'); odt_to_pdf(src,os.path.join(folder('pdf'),out)); res=file_result('pdf',out,cid)
        elif cid=='epub_to_pdf': out=output_name(name,'pdf'); ebook_to_pdf(src,os.path.join(folder('pdf'),out)); res=file_result('pdf',out,cid)
        elif cid=='epub_to_mobi': out=output_name(name,'mobi'); epub_to_mobi(src,os.path.join(folder('archive'),out)); res=file_result('archive',out,cid)
        elif cid=='mobi_to_pdf': out=output_name(name,'pdf'); mobi_to_pdf(src,os.path.join(folder('pdf'),out)); res=file_result('pdf',out,cid)
        elif cid=='zip_extract': dest=os.path.join(folder('archive'),uuid.uuid4().hex[:10]); extract_zip(src,dest); res={'success':True,'message':'ZIP extracted successfully.','folder':dest}
        elif cid=='compress_pdf': out=output_name(name,'pdf'); compress_pdf(src,os.path.join(folder('pdf'),out)); res=file_result('pdf',out,cid)
        elif cid=='split_pdf':
            outdir=os.path.join(folder('pdf'),uuid.uuid4().hex[:10]); os.makedirs(outdir,exist_ok=True); fs=split_pdf(src,outdir,1); links=[{'filename':f,'download_url':f'/api/download/pdf/{os.path.basename(outdir)}/{f}'} for f in fs]; res={'success':True,'files':links,'file':links[0] if links else None}
        else: return jsonify({'success':False,'error':'This conversion is not implemented.'}),400
        if res.get('note') is None: res.pop('note',None)
        add_history(name,cid,res.get('file',{}).get('filename') if res.get('file') else None)
        return jsonify(res)
    except Exception as e:
        return jsonify({'success':False,'error':str(e)}),400

@conversion_bp.post('/merge-pdf')
def merge_pdf():
    d=request.get_json(silent=True) or {}; names=d.get('filenames',[])
    if len(names)<2:return jsonify({'success':False,'error':'At least two PDF files are required.'}),400
    paths=[uploaded(x) for x in names]
    if any(not p for p in paths):return jsonify({'success':False,'error':'One or more PDFs were not found.'}),404
    out=output_name('Merged_PDF.pdf','pdf','Merged_PDF'); merge_pdf_files(paths,os.path.join(folder('pdf'),out)); add_history(', '.join(names),'merge_pdf',out); return jsonify(file_result('pdf',out,'merge_pdf'))

@conversion_bp.post('/pdf-operation')
def pdf_operation():
    d=request.get_json(silent=True) or {}; name=d.get('filename',''); src=uploaded(name)
    if not src:return jsonify({'success':False,'error':'PDF not found.'}),404
    op=d.get('operation'); out=output_name(name,'pdf',op); outpath=os.path.join(folder('pdf'),out)
    try:
        if op=='unlock_pdf':
            password=str(d.get('password',''))
            doc=pymupdf.open(src)
            if doc.needs_pass:
                if not password or not doc.authenticate(password):
                    doc.close(); raise ValueError('Password is required or incorrect.')
            doc.save(outpath); doc.close(); return jsonify(file_result('pdf',out,op))
        if op=='encrypt_pdf':
            password=str(d.get('password','')).strip()
            if len(password)<4: raise ValueError('Password must contain at least 4 characters.')
            doc=pymupdf.open(src); doc.save(outpath,encryption=pymupdf.PDF_ENCRYPT_AES_256,user_pw=password,owner_pw=password); doc.close(); return jsonify(file_result('pdf',out,op))
        doc=pymupdf.open(src)
        if op=='rotate':
            pages=d.get('pages') or list(range(doc.page_count)); deg=int(d.get('degrees',90))
            for i in pages:
                if 0<=int(i)<doc.page_count: doc[int(i)].set_rotation((doc[int(i)].rotation+deg)%360)
            doc.save(outpath)
        elif op=='delete_pages':
            pages=sorted(set(int(x)-1 for x in d.get('pages',[])),reverse=True)
            if not pages: raise ValueError('Select at least one page.')
            if len(pages)>=doc.page_count: raise ValueError('At least one page must remain.')
            for i in pages:
                if 0<=i<doc.page_count: doc.delete_page(i)
            doc.save(outpath)
        elif op=='extract_pages':
            pages=[int(x)-1 for x in d.get('pages',[])]; new=pymupdf.open()
            for i in pages:
                if 0<=i<doc.page_count:new.insert_pdf(doc,from_page=i,to_page=i)
            if not new.page_count: raise ValueError('No valid pages selected.')
            new.save(outpath); new.close()
        elif op=='reorder_pages':
            order=[int(x)-1 for x in d.get('order',[])]
            if sorted(order)!=list(range(doc.page_count)): raise ValueError('Order must contain every page exactly once.')
            new=pymupdf.open()
            for i in order:new.insert_pdf(doc,from_page=i,to_page=i)
            new.save(outpath); new.close()
        elif op=='page_numbers':
            start=int(d.get('start',1)); pos=d.get('position','bottom-right')
            for n,p in enumerate(doc):
                x=30 if 'left' in pos else p.rect.width-55; y=25 if 'top' in pos else p.rect.height-18; p.insert_text((x,y),str(start+n),fontsize=9,color=(.25,.3,.4))
            doc.save(outpath)
        elif op=='watermark':
            text=str(d.get('text','CONFIDENTIAL')).strip() or 'CONFIDENTIAL'
            for p in doc:p.insert_textbox(p.rect,text,fontsize=42,align=pymupdf.TEXT_ALIGN_CENTER,color=(.75,.78,.85),fill_opacity=.18)
            doc.save(outpath)
        elif op=='split':
            outdir=os.path.join(folder('pdf'),uuid.uuid4().hex[:10]); os.makedirs(outdir,exist_ok=True); files=split_pdf(src,outdir,int(d.get('pages_per_file',1)),d.get('page_spec') or None); doc.close(); links=[{'filename':f,'download_url':f'/api/download/pdf/{os.path.basename(outdir)}/{f}'} for f in files]; return jsonify({'success':True,'file':links[0] if links else None,'files':links})
        elif op=='extract_images':
            archive=output_name(name,'zip','extracted_images'); archive_path=os.path.join(folder('archive'),archive); tmp=os.path.join(Config.INSTANCE_FOLDER,uuid.uuid4().hex); os.makedirs(tmp,exist_ok=True); files=[]
            for pi,p in enumerate(doc):
                for ii,img in enumerate(p.get_images(full=True)):
                    pix=pymupdf.Pixmap(doc,img[0]); fp=os.path.join(tmp,f'page_{pi+1}_image_{ii+1}.png'); pix.save(fp); pix.close(); files.append(fp)
            with zipfile.ZipFile(archive_path,'w',zipfile.ZIP_DEFLATED) as z:
                for fp in files:z.write(fp,os.path.basename(fp))
            doc.close(); return jsonify({'success':True,'file':{'filename':archive,'download_url':f'/api/download/archive/{archive}'}})
        else: raise ValueError('Unsupported PDF operation.')
        doc.close(); add_history(name,op,out); return jsonify(file_result('pdf',out,op))
    except Exception as e:
        return jsonify({'success':False,'error':str(e)}),400

@conversion_bp.post('/multi-convert')
def multi_convert():
    d=request.get_json(silent=True) or {}; names=d.get('filenames') or []; cid=str(d.get('conversion_id','')).strip()
    if not names: return jsonify({'success':False,'error':'Select at least one file.'}),400
    paths=[uploaded(x) for x in names]
    if any(not p for p in paths): return jsonify({'success':False,'error':'One or more uploaded files were not found.'}),404
    try:
        if cid=='images_to_pdf':
            out=output_name(names[0],'pdf','images_to_pdf'); convert_images_to_pdf(paths,os.path.join(folder('pdf'),out)); res=file_result('pdf',out,cid)
        elif cid=='images_to_word':
            out=output_name(names[0],'docx','images_to_word'); convert_images_to_word(paths,os.path.join(folder('word'),out)); res=file_result('word',out,cid)
        elif cid=='gif_maker':
            out=output_name(names[0],'gif','animated'); make_gif(paths,os.path.join(folder('image'),out),duration=int(d.get('duration',350))); res=file_result('image',out,cid)
        else:
            return jsonify({'success':False,'error':'Unsupported multi-file operation.'}),400
        add_history(', '.join(names),cid,res.get('file',{}).get('filename')); return jsonify(res)
    except Exception as e: return jsonify({'success':False,'error':str(e)}),400
