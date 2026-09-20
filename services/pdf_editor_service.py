import json,os,shutil,uuid
from datetime import datetime
import pymupdf
from config import Config

def session_dir(sid):
 p=os.path.join(Config.EDITOR_FOLDER,sid);os.makedirs(p,exist_ok=True);return p

def load_state(sid):
 with open(os.path.join(session_dir(sid),'state.json'),encoding='utf-8') as f:return json.load(f)

def save_state(sid,state):
 with open(os.path.join(session_dir(sid),'state.json'),'w',encoding='utf-8') as f:json.dump(state,f,indent=2)

def create_session(source,original):
 sid=uuid.uuid4().hex;d=session_dir(sid);cur=os.path.join(d,'current.pdf');shutil.copy2(source,cur)
 st={'id':sid,'original_name':original,'current':cur,'undo':[],'redo':[],'created':datetime.now().isoformat(timespec='seconds')};save_state(sid,st);return st

def snapshot(sid):
 st=load_state(sid);p=os.path.join(session_dir(sid),f'undo_{uuid.uuid4().hex}.pdf');shutil.copy2(st['current'],p);st['undo'].append(p);st['undo']=st['undo'][-30:]
 for r in st['redo']:
  try:os.remove(r)
  except OSError:pass
 st['redo']=[];save_state(sid,st)

def doc(sid):return pymupdf.open(load_state(sid)['current'])

def commit(sid,d):
 cur=load_state(sid)['current'];tmp=cur+'.tmp';d.save(tmp,garbage=4,clean=True,deflate=True);d.close();os.replace(tmp,cur)

def page_info(d):return [{'number':i+1,'width':round(p.rect.width,2),'height':round(p.rect.height,2),'rotation':p.rotation} for i,p in enumerate(d)]

def _span_records(page):
 records=[]
 for block in page.get_text('dict').get('blocks',[]):
  if block.get('type') != 0: continue
  for line in block.get('lines',[]):
   for sp in line.get('spans',[]):
    if sp.get('text','').strip():
     records.append({'text':sp['text'],'bbox':list(sp['bbox']),'font':sp.get('font','helv'),'size':round(sp.get('size',11),2),'color':sp.get('color',0),'flags':sp.get('flags',0),'origin':sp.get('origin',[sp['bbox'][0],sp['bbox'][3]])})
 return records

def spans(page):return _span_records(page)

def _font_xrefs(page):
 out={}
 for f in page.get_fonts(full=True):
  # tuple: xref, ext, type, basefont, name, encoding, ...
  if len(f)>=5:
   xref,base=f[0],f[3]
   out[str(base).lower()]=xref
   out[str(f[4]).lower()]=xref
 return out

def words(page):
 spans_list=_span_records(page);fx=_font_xrefs(page);out=[]
 for item in page.get_text('words') or []:
  x0,y0,x1,y1,text,block,line,word_no=item[:8]
  if not str(text).strip():continue
  best=None;best_area=None
  for sp in spans_list:
   sx0,sy0,sx1,sy1=sp['bbox'];ix0=max(x0,sx0);iy0=max(y0,sy0);ix1=min(x1,sx1);iy1=min(y1,sy1);area=max(0,ix1-ix0)*max(0,iy1-iy0)
   if area and (best_area is None or area>best_area):best,best_area=sp,area
  style=best or {'font':'helv','size':11,'color':0,'flags':0}
  fontname=style.get('font','helv');xref=fx.get(fontname.lower())
  if xref is None:
   for k,v in fx.items():
    if k and (k in fontname.lower() or fontname.lower() in k):xref=v;break
  out.append({'text':str(text),'bbox':[float(x0),float(y0),float(x1),float(y1)],'font':fontname,'size':style.get('size',11),'color':style.get('color',0),'flags':style.get('flags',0),'font_xref':xref,'block':int(block),'line':int(line),'word':int(word_no)})
 return out

def col(v):
 if isinstance(v,(list,tuple)):return tuple(float(x) for x in v[:3])
 n=int(v or 0);return (((n>>16)&255)/255,((n>>8)&255)/255,(n&255)/255)

def font(v):
 v=(v or '').lower()
 if 'times' in v or 'serif' in v:return 'times-bolditalic' if 'bold' in v and 'italic' in v else ('times-bold' if 'bold' in v else ('times-italic' if 'italic' in v else 'times-roman'))
 if 'courier' in v or 'mono' in v:return 'courier-bold' if 'bold' in v else 'courier'
 return 'hebi' if 'bold' in v and 'italic' in v else ('hebo' if 'bold' in v else ('heit' if 'italic' in v else 'helv'))

def _embedded_font(doc_obj,page,font_xref):
 if not font_xref:return None
 try:
  info=doc_obj.extract_font(int(font_xref))
  buf=info[3] if len(info)>3 else None
  if buf:
   ext=(info[1] or 'ttf').lower().lstrip('.')
   path=os.path.join(session_dir(load_state_from_doc(doc_obj)),'embedded_'+str(font_xref)+'.'+ext) if False else None
 except Exception:return None
 return None

def _font_file_for_span(d,page,font_xref,sid):
 if not font_xref:return None
 path=os.path.join(session_dir(sid),f'font_{font_xref}.bin')
 if os.path.exists(path):return path
 try:
  info=d.extract_font(int(font_xref));buf=info[3]
  if buf:
   ext=(info[1] or 'ttf').lower().lstrip('.')
   path=os.path.join(session_dir(sid),f'font_{font_xref}.{ext}')
   with open(path,'wb') as f:f.write(buf)
   return path
 except Exception:pass
 return None

def replace_span(sid,page,bbox,text,size,color,fontname,font_xref=None):
 text=str(text if text is not None else '')
 if not text.strip():raise ValueError('Text cannot be empty.')
 vals=[float(v) for v in bbox]
 if len(vals)!=4 or not all(map(lambda v: v==v and abs(v)<1e7,vals)):raise ValueError('Text box must be finite.')
 x0,y0,x1,y1=vals
 if x1<=x0 or y1<=y0:raise ValueError('Text box must have positive width and height.')
 snapshot(sid);d=doc(sid);p=d[page];r=pymupdf.Rect(x0,y0,x1,y1)
 # Remove only the selected word/box. Keep graphics and images intact.
 p.add_redact_annot(r,fill=(1,1,1),cross_out=False);p.apply_redactions(images=0,graphics=0,text=0)
 fs=max(1.0,float(size));native_font=font(fontname)
 fontfile=_font_file_for_span(d,p,font_xref,sid)
 # Preserve the original baseline/height and calculate a natural width for the replacement.
 desired=pymupdf.get_text_length(text,fontname=native_font,fontsize=fs)
 if fontfile:
  try:
   tempname='__hyper_edit_font'
   p.insert_font(fontname=tempname,fontfile=fontfile)
   native_font=tempname
   desired=pymupdf.get_text_length(text,fontname=native_font,fontsize=fs)
  except Exception:pass
 # Never squeeze the replacement into the old word width. Grow to the right while respecting page edge.
 avail=max(8.0,p.rect.width-x0-2)
 width=max(float(x1-x0),desired+2.0)
 width=min(width,avail)
 # If text is still too wide, reduce font size only as a last resort, retaining the user's requested size when possible.
 while desired>avail and fs>4:
  fs=max(4.0,fs-0.25)
  desired=pymupdf.get_text_length(text,fontname=native_font,fontsize=fs)
  if desired<=avail:break
 width=min(max(float(x1-x0),desired+2.0),avail)
 # Use a tight line box around the original baseline.
 top=max(0.0,y0-1.5);bottom=min(p.rect.height,max(y1+2.0,top+fs*1.25))
 rr=pymupdf.Rect(x0,top,x0+width,bottom)
 result=p.insert_textbox(rr,text,fontname=native_font,fontsize=fs,color=col(color),overlay=True,align=0)
 if result<0:
  # Retry with a slightly taller box; do not silently leave a half-edit behind.
  rr=pymupdf.Rect(x0,max(0,y0-fs*0.25),x0+width,min(p.rect.height,y1+fs*1.1))
  result=p.insert_textbox(rr,text,fontname=native_font,fontsize=fs,color=col(color),overlay=True,align=0)
 if result<0:
  d.close()
  raise ValueError('Replacement text does not fit. Reduce the font size or widen the text box.')
 commit(sid,d)

def add_text(sid,page,bbox,text,size,color):
 text=str(text if text is not None else '').strip()
 if not text:raise ValueError('Text cannot be empty.')
 vals=[float(v) for v in bbox]
 if len(vals)!=4 or not all(v==v and abs(v)<1e7 for v in vals):raise ValueError('Text box must be finite.')
 x0,y0,x1,y1=vals
 if x1<=x0 or y1<=y0:raise ValueError('Text box must have positive width and height. Drag to create a text box.')
 snapshot(sid);d=doc(sid);p=d[page];r=pymupdf.Rect(vals)
 result=p.insert_textbox(r,text,fontname='helv',fontsize=float(size),color=col(color),overlay=True)
 if result<0:
  d.close();raise ValueError('Text does not fit inside the text box. Make the box wider or taller.')
 commit(sid,d)

def annotate(sid,page,bbox,kind,color):
 snapshot(sid);d=doc(sid);fn={'highlight':d[page].add_highlight_annot,'underline':d[page].add_underline_annot,'strikeout':d[page].add_strikeout_annot}[kind];a=fn(pymupdf.Rect(bbox));a.set_colors(stroke=col(color));a.update();commit(sid,d)

def redact(sid,page,bbox):
 snapshot(sid);d=doc(sid);p=d[page];p.add_redact_annot(pymupdf.Rect(bbox),fill=(1,1,1),cross_out=False);p.apply_redactions();commit(sid,d)

def shape(sid,page,kind,bbox,color,fill,width):
 snapshot(sid);d=doc(sid);p=d[page];r=pymupdf.Rect(bbox);c=col(color);f=col(fill) if fill else None
 if kind=='rectangle':p.draw_rect(r,color=c,fill=f,width=float(width))
 elif kind=='ellipse':p.draw_oval(r,color=c,fill=f,width=float(width))
 else:p.draw_line(r.tl,r.br,color=c,width=float(width))
 commit(sid,d)

def freehand(sid,page,points,color,width):
 if len(points)<2:return
 snapshot(sid);d=doc(sid);p=d[page]
 for a,b in zip(points,points[1:]):p.draw_line(a,b,color=col(color),width=float(width))
 commit(sid,d)

def insert_image(sid,page,bbox,path):
 snapshot(sid);d=doc(sid);d[page].insert_image(pymupdf.Rect(bbox),filename=path,keep_proportion=True);commit(sid,d)

def page_op(sid,op,**kw):
 snapshot(sid);d=doc(sid)
 if op=='rotate':
  for i in kw['pages']:
   if 0<=i<d.page_count:d[i].set_rotation((d[i].rotation+kw['degrees'])%360)
 elif op=='delete':
  for i in sorted(set(kw['pages']),reverse=True):
   if 0<=i<d.page_count:d.delete_page(i)
 elif op=='duplicate':d.copy_page(kw['page'],kw['page']+1)
 elif op=='add_blank':
  after=kw.get('after',d.page_count-1);r=d[after].rect if d.page_count else pymupdf.Rect(0,0,595,842);d.new_page(pno=after+1,width=r.width,height=r.height)
 elif op=='reorder':
  order=kw['order'];new=pymupdf.open()
  for i in order:new.insert_pdf(d,from_page=i,to_page=i)
  d.close();new.save(load_state(sid)['current']+'.tmp',garbage=4,clean=True);new.close();os.replace(load_state(sid)['current']+'.tmp',load_state(sid)['current']);return
 commit(sid,d)

def undo(sid):
 st=load_state(sid)
 if not st['undo']:return False
 cur=st['current'];snap=st['undo'].pop();redo_path=os.path.join(session_dir(sid),f'redo_{uuid.uuid4().hex}.pdf');shutil.copy2(cur,redo_path);shutil.copy2(snap,cur);st['redo'].append(redo_path);save_state(sid,st);return True

def redo(sid):
 st=load_state(sid)
 if not st['redo']:return False
 cur=st['current'];snap=st['redo'].pop();undo_path=os.path.join(session_dir(sid),f'undo_{uuid.uuid4().hex}.pdf');shutil.copy2(cur,undo_path);shutil.copy2(snap,cur);st['undo'].append(undo_path);save_state(sid,st);return True
