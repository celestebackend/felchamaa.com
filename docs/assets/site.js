
const header=document.querySelector('.header');
if(header)addEventListener('scroll',()=>header.classList.toggle('scrolled',scrollY>18),{passive:true});
const menuButton=document.querySelector('.menu-button'),mobileMenu=document.querySelector('.mobile-menu');
if(menuButton&&mobileMenu){menuButton.addEventListener('click',()=>{const open=mobileMenu.classList.toggle('open');menuButton.setAttribute('aria-expanded',String(open));menuButton.textContent=open?'Close':'Menu';document.body.style.overflow=open?'hidden':''});mobileMenu.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{mobileMenu.classList.remove('open');menuButton.setAttribute('aria-expanded','false');menuButton.textContent='Menu';document.body.style.overflow=''}));}
const viewer=document.getElementById('viewer');
if(viewer){
  const image=document.getElementById('viewer-image'),title=document.getElementById('viewer-title'),meta=document.getElementById('viewer-meta'),close=document.getElementById('viewer-close');
  const works=[...document.querySelectorAll('.js-view')];
  let prior=null,current=0,touchX=0,touchY=0;
  const show=index=>{
    current=(index+works.length)%works.length;
    const button=works[current],source=button.querySelector('img');
    image.src=source.currentSrc||source.src;
    image.alt=source.alt;
    title.textContent=button.dataset.title;
    meta.textContent=button.dataset.meta;
    [works[(current+1)%works.length],works[(current-1+works.length)%works.length]].forEach(item=>{const src=item?.querySelector('img')?.src;if(src)(new Image()).src=src});
  };
  works.forEach((button,index)=>button.addEventListener('click',()=>{prior=button;show(index);viewer.classList.add('open');document.body.style.overflow='hidden';close.focus()}));
  const shut=()=>{viewer.classList.remove('open');document.body.style.overflow='';prior?.focus()};
  close.addEventListener('click',shut);
  viewer.addEventListener('click',event=>{if(event.target===viewer)shut()});
  viewer.addEventListener('touchstart',event=>{const touch=event.changedTouches[0];touchX=touch.clientX;touchY=touch.clientY},{passive:true});
  viewer.addEventListener('touchend',event=>{if(!viewer.classList.contains('open'))return;const touch=event.changedTouches[0],dx=touch.clientX-touchX,dy=touch.clientY-touchY;if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy)){show(current+(dx<0?1:-1))}},{passive:true});
  addEventListener('keydown',event=>{if(!viewer.classList.contains('open'))return;if(event.key==='Escape')shut();if(event.key==='ArrowRight')show(current+1);if(event.key==='ArrowLeft')show(current-1)});
}
