document.addEventListener('DOMContentLoaded',()=>{
 const input=document.getElementById('allToolsFile'), toast=document.getElementById('toolToast'); let current=null;
 const multiIds=new Set(['merge_pdf','gif_maker','images_to_pdf']);
 document.querySelectorAll('.mega-tool').forEach(btn=>btn.addEventListener('click',()=>{current=btn.dataset.id; if(current==='edit_pdf'||current==='edit_word') input.accept=current==='edit_pdf'?'.pdf':'.docx'; else input.accept=''; input.multiple=multiIds.has(current); input.click();}));
 input.addEventListener('change',async()=>{const files=[...input.files]; if(!files.length)return; setBusy(true); try{ if(current==='edit_pdf'||current==='edit_word'){const up=await upload(files[0]); location.href=(current==='edit_pdf'?'/pdf-editor?filename=':'/word-editor?filename=')+encodeURIComponent(up.filename);return;} const ups=[]; for(const f of files) ups.push(await upload(f)); if(current==='merge_pdf'){const r=await post('/api/merge-pdf',{filenames:ups.map(x=>x.filename)}); return showResult(r,'Combine PDF');} if(current==='gif_maker'||current==='images_to_pdf'){const r=await post('/api/multi-convert',{filenames:ups.map(x=>x.filename),conversion_id:current}); return showResult(r,current==='gif_maker'?'GIF Maker':'Images to PDF');} const u=ups[0]; if(current==='split_pdf'||current==='rotate_pdf'||current==='delete_pages'||current==='reorder_pages'||current==='page_numbers'||current==='watermark_pdf'||current==='extract_images'||current==='unlock_pdf'||current==='encrypt_pdf'){return await runPdfTool(u.filename,current);} const r=await post('/api/convert',{filename:u.filename,conversion_id:current}); showResult(r,current.replaceAll('_',' ')); }catch(e){show(e.message,true); const result=document.getElementById('toolResult'); if(result){result.innerHTML=`<div class="tool-result error"><strong>Operation failed</strong><span>${esc(e.message)}</span></div>`; result.hidden=false;}} finally{setBusy(false); input.value='';} });
 async function runPdfTool(filename,id){let payload={filename,operation:id.replace('_pdf','')}; if(id==='split_pdf'){payload.operation='split';payload.pages_per_file=1;} if(id==='rotate_pdf'){payload.operation='rotate';payload.degrees=90;} if(id==='delete_pages'){const p=prompt('Pages to delete, e.g. 2,4-6:','');if(!p)return;payload.pages=parsePages(p);} if(id==='reorder_pages'){const p=prompt('New order, e.g. 3,1,2:','');if(!p)return;payload.order=parsePages(p);} if(id==='page_numbers'){payload.operation='page_numbers';payload.position=prompt('Position: bottom-right, bottom-left, top-right or top-left:','bottom-right')||'bottom-right';payload.start=1;} if(id==='watermark_pdf'){payload.operation='watermark';payload.text=prompt('Watermark text:','CONFIDENTIAL')||'CONFIDENTIAL';} if(id==='unlock_pdf'){payload.operation='unlock_pdf';payload.password=prompt('Enter the PDF password:','');} if(id==='encrypt_pdf'){payload.operation='encrypt_pdf';payload.password=prompt('Set a password (minimum 4 characters):','');} const r=await post('/api/pdf-operation',payload);showResult(r,id.replaceAll('_',' '));}
 async function upload(file){const fd=new FormData();fd.append('file',file);const r=await fetch('/api/upload',{method:'POST',body:fd});const d=await r.json();if(!d.success)throw Error(d.error);return d.file;}
 async function post(url,data){const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});const d=await r.json();if(!d.success)throw Error(d.error||'Operation failed');return d;}
 function showResult(d,name){
  const result=document.getElementById('toolResult');
  const links=[];
  if(d.file && d.file.download_url) links.push(d.file);
  if(Array.isArray(d.files)) d.files.forEach(x=>{if(x && x.download_url && !links.some(y=>y.download_url===x.download_url)) links.push(x)});
  const title=(name||'Operation').replaceAll('_',' ');
  if(!result){
    if(links[0]) window.open(links[0].download_url,'_blank');
    return;
  }
  if(!links.length){
    result.innerHTML=`<div class="tool-result error"><strong>${esc(title)} did not return a downloadable file.</strong><span>${esc(d.note||d.message||'No output file was returned.')}</span></div>`;
    result.hidden=false;
    return;
  }
  result.innerHTML=`<div class="tool-result success"><div><strong>${esc(title)} completed</strong><span>${esc(d.note||'Your file is ready.')}</span></div><div class="tool-result-actions">${links.map((x,i)=>`<a class="tool-download" href="${x.download_url}" download>${i===0?'Download result ↓':'Download '+esc(x.filename)}</a>`).join('')}</div></div>`;
  result.hidden=false;
  // Start the download automatically, while keeping visible download buttons.
  setTimeout(()=>{const a=document.createElement('a');a.href=links[0].download_url;a.download=links[0].filename||'';a.rel='noopener';document.body.appendChild(a);a.click();a.remove();},80);
 }
 function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
 function show(m,isError=false){const toast=document.getElementById('toolToast');toast.textContent=m;toast.classList.toggle('error',!!isError);toast.hidden=false;clearTimeout(window._tt);window._tt=setTimeout(()=>toast.hidden=true,5000)}
 function setBusy(v){document.querySelectorAll('.mega-tool').forEach(b=>b.disabled=v)}
 function parsePages(s){return String(s||'').split(',').flatMap(x=>{x=x.trim();if(!x)return[];if(x.includes('-')){let[a,b]=x.split('-').map(Number),o=[];for(let i=Math.min(a,b);i<=Math.max(a,b);i++)o.push(i);return o}return [Number(x)]}).filter(Boolean)}
});
