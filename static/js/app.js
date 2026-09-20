document.addEventListener('DOMContentLoaded',()=>{
  document.querySelectorAll('a[href=""]').forEach(a=>a.removeAttribute('href'));
});
