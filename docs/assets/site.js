
const header=document.querySelector('.header');
if(header)addEventListener('scroll',()=>header.classList.toggle('scrolled',scrollY>18),{passive:true});
const menuButton=document.querySelector('.menu-button'),mobileMenu=document.querySelector('.mobile-menu');
if(menuButton&&mobileMenu){menuButton.addEventListener('click',()=>{const open=mobileMenu.classList.toggle('open');menuButton.setAttribute('aria-expanded',String(open));menuButton.textContent=open?'Close':'Menu';document.body.style.overflow=open?'hidden':''});mobileMenu.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{mobileMenu.classList.remove('open');menuButton.setAttribute('aria-expanded','false');menuButton.textContent='Menu';document.body.style.overflow=''}));}
document.querySelectorAll('.gallery').forEach(gallery=>{
  const buckets={landscape:[],square:[],portrait:[],small:[]};
  [...gallery.querySelectorAll('.work')].forEach(work=>{
    const meta=work.querySelector('.js-view')?.dataset.meta||'';
    const dimensions=meta.match(/([0-9.]+)\s*×\s*([0-9.]+)\s*cm/i);
    let group='landscape';
    if(dimensions){
      const height=Number(dimensions[1]),width=Number(dimensions[2]);
      if(height<=30&&width<=30)group='small';
      else if(Math.abs(height-width)/Math.max(height,width)<=.08)group='square';
      else group=height>width?'portrait':'landscape';
    }
    buckets[group].push(work);
  });
  const labels={landscape:'Landscape-format paintings',square:'Large square-format paintings',portrait:'Portrait-format paintings',small:'Paintings measuring 30 × 30 cm or less'};
  const sections=['landscape','square','portrait','small'].filter(group=>buckets[group].length).map(group=>{
    const section=document.createElement('section');
    section.className=`format-group format-group-${group}`;
    section.setAttribute('aria-label',labels[group]);
    section.append(...buckets[group]);
    return section;
  });
  gallery.replaceChildren(...sections);
  gallery.classList.add('grouped-gallery');
});
const viewer=document.getElementById('viewer');
if(viewer){
  const image=document.getElementById('viewer-image'),media=viewer.querySelector('.viewer-media'),title=document.getElementById('viewer-title'),meta=document.getElementById('viewer-meta'),close=document.getElementById('viewer-close'),previous=document.getElementById('viewer-prev'),next=document.getElementById('viewer-next');
  const works=[...document.querySelectorAll('.js-view')];
  let prior=null,current=0,touchX=0,touchY=0,mouseX=0,mouseY=0,wheelX=0,wheelTimer=null;
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
  previous?.addEventListener('click',()=>show(current-1));
  next?.addEventListener('click',()=>show(current+1));
  viewer.addEventListener('click',event=>{if(event.target===viewer)shut()});
  viewer.addEventListener('touchstart',event=>{const touch=event.changedTouches[0];touchX=touch.clientX;touchY=touch.clientY},{passive:true});
  viewer.addEventListener('touchend',event=>{if(!viewer.classList.contains('open'))return;const touch=event.changedTouches[0],dx=touch.clientX-touchX,dy=touch.clientY-touchY;if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy)){show(current+(dx<0?1:-1))}},{passive:true});
  media.addEventListener('pointerdown',event=>{if(event.pointerType!=='mouse'||event.button!==0)return;mouseX=event.clientX;mouseY=event.clientY;media.classList.add('dragging')});
  media.addEventListener('pointerup',event=>{if(event.pointerType!=='mouse'||!media.classList.contains('dragging'))return;media.classList.remove('dragging');const dx=event.clientX-mouseX,dy=event.clientY-mouseY;if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy))show(current+(dx<0?1:-1))});
  media.addEventListener('pointercancel',()=>media.classList.remove('dragging'));
  media.addEventListener('dragstart',event=>event.preventDefault());
  media.addEventListener('wheel',event=>{if(Math.abs(event.deltaX)<=Math.abs(event.deltaY))return;wheelX+=event.deltaX;clearTimeout(wheelTimer);wheelTimer=setTimeout(()=>wheelX=0,180);if(Math.abs(wheelX)>60){show(current+(wheelX>0?1:-1));wheelX=0}},{passive:true});
  addEventListener('keydown',event=>{if(!viewer.classList.contains('open'))return;if(event.key==='Escape')shut();if(event.key==='ArrowRight')show(current+1);if(event.key==='ArrowLeft')show(current-1)});
}
