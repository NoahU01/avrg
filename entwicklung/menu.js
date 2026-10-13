/* Entwicklungsmenü „/ Entwicklung /“ – NUR auf Daniels Branch, NIE auf main.
   Neue Unterseiten nur hier in MENU eintragen; alle Seiten holen das Menü aus dieser Datei.
   Aufbau und Verhalten wie im empiria-Repo (werkzeuge/entwicklung-menu.*). */
(function(){
var MENU =
'<div class="dev-dd" data-dev-dd>'+
'<button class="dev-dd-toggle" type="button" aria-expanded="false"><span class="dev-dd-long">/ Entwicklung /</span><span class="dev-dd-short" aria-hidden="true">/ Entw. /</span><svg class="dev-dd-chev" viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></button>'+
'<div class="dev-dd-panel">'+
'<p class="dev-dd-note"><b>Nur in der Entwicklungsumgebung sichtbar</b>Dieser Menüpunkt ist in der Live-Version nicht enthalten.</p>'+
'<p class="dev-dd-group">Unterseiten</p>'+
'<div class="dev-dd-sub">'+
'<a href="/entwicklung/corporate-design.html" class="dev-dd-link dev-dd-link--parent"><span class="dev-dd-tag">CD</span><span class="dev-dd-txt"><b>Corporate Design</b><small>SV Owen &middot; Vorlagen</small></span></a>'+
'<div class="dev-dd-flyout"><div class="dev-dd-flyout-panel">'+
'<p class="dev-dd-group">Vorlagen</p>'+
'<a href="/entwicklung/powerpoint-master.html" class="dev-dd-link"><span class="dev-dd-tag">PPT</span><span class="dev-dd-txt"><b>PowerPoint-Master</b><small>SV Owen &middot; in Arbeit</small></span></a>'+
'</div></div>'+
'</div>'+
'</div>'+
'</div>';

function einsetzen(){
var brand=document.querySelector('.site-header .brand');
if(!brand||document.querySelector('[data-dev-dd]'))return;
brand.insertAdjacentHTML('afterend',MENU);
}

function init(){
einsetzen();
var here=location.href.split('#')[0].split('?')[0];
document.querySelectorAll('[data-dev-dd]').forEach(function(d){
var b=d.querySelector('.dev-dd-toggle'),t;
function desk(){return window.innerWidth>900;}
function set(o){d.classList.toggle('is-open',o);b.setAttribute('aria-expanded',String(o));}
b.addEventListener('click',function(e){e.stopPropagation();set(desk()&&d.matches(':hover')?true:!d.classList.contains('is-open'));});
d.addEventListener('mouseenter',function(){if(desk()){clearTimeout(t);set(true);}});
d.addEventListener('mouseleave',function(){if(desk()){t=setTimeout(function(){set(false);},180);}});
document.addEventListener('click',function(e){if(!d.contains(e.target))set(false);});
document.addEventListener('keydown',function(e){if(e.key==='Escape')set(false);});
d.querySelectorAll('.dev-dd-link').forEach(function(a){if(a.href&&a.href.split('#')[0]===here)a.classList.add('is-current');});
var panel=d.querySelector('.dev-dd-panel');

// ---- Zweite Ebene -------------------------------------------------------
// Das Panel muss scrollen, seit es vier Kategorien hat (gemessen: 834px
// Inhalt bei 680px Platz auf einem 900er Bildschirm). Ein Flyout darin wuerde
// mitgeschnitten. position:fixed hilft nicht - die Kopfzeile hat einen
// backdrop-filter und wird dadurch zum Bezugsrahmen fuer fixed. Das Flyout
// haengt sich beim Oeffnen deshalb unter .dev-dd um: dort ist es absolut
// positioniert, aber ausserhalb des scrollenden Panels.
// Weil :hover dort nicht mehr traegt, steuert eine Klasse die Sichtbarkeit.
panel&&panel.querySelectorAll(':scope>.dev-dd-sub').forEach(function(s){
var f=s.querySelector(':scope>.dev-dd-flyout');if(!f)return;
var heim=f.parentNode,nachbar=f.nextSibling,t2;
function heimholen(){
clearTimeout(t2);f.classList.remove('is-auf');s.classList.remove('is-auf');
if(f.parentNode!==heim){heim.insertBefore(f,nachbar);f.removeAttribute('style');}
}
function auf(){
if(!desk()){heimholen();return;}
clearTimeout(t2);
if(f.parentNode!==d)d.appendChild(f);
var z=s.getBoundingClientRect(),dr=d.getBoundingClientRect(),
    k=f.firstElementChild.getBoundingClientRect();
// Rechts daneben, wenn Platz ist - sonst nach links gekippt.
if(z.right+10+k.width>window.innerWidth-12){
f.style.left=(z.left-dr.left-10-k.width)+'px';
f.style.paddingLeft='0';f.style.paddingRight='10px';
}else{
f.style.left=(z.right-dr.left)+'px';
f.style.paddingLeft='';f.style.paddingRight='';
}
// Senkrecht an der Zeile, aber nie unter den Fensterrand.
var oben=z.top-dr.top-10,grenze=window.innerHeight-12-k.height-dr.top;
f.style.top=Math.max(-dr.top+12,Math.min(oben,grenze))+'px';
f.classList.add('is-auf');s.classList.add('is-auf');
}
function zu(){t2=setTimeout(function(){f.classList.remove('is-auf');s.classList.remove('is-auf');},180);}
s.addEventListener('mouseenter',auf);
s.addEventListener('focusin',auf);
s.addEventListener('mouseleave',zu);
f.addEventListener('mouseenter',function(){clearTimeout(t2);});
f.addEventListener('mouseleave',zu);
panel.addEventListener('scroll',function(){if(f.classList.contains('is-auf'))auf();});
window.addEventListener('resize',heimholen);
});

// ---- Dritte Ebene -------------------------------------------------------
// Die bleibt, wo sie ist: ihr Elternteil ist bereits aus dem Panel heraus,
// dort wird nichts mehr abgeschnitten. Sie braucht nur die Kippung nach
// links, weil rechts neben der zweiten Ebene kein Platz mehr ist.
d.querySelectorAll('.dev-dd-flyout .dev-dd-sub').forEach(function(s){
var f=s.querySelector(':scope>.dev-dd-flyout');if(!f)return;
function platzieren(){
f.style.top='';f.style.left='';f.style.right='';f.style.paddingLeft='';f.style.paddingRight='';
if(!desk())return;
f.style.top='-10px';
var r=f.firstElementChild.getBoundingClientRect(),z=s.getBoundingClientRect();
if(z.right+10+r.width>window.innerWidth-12){
f.style.left='auto';f.style.right='100%';
f.style.paddingLeft='0';f.style.paddingRight='10px';
}
var u=f.getBoundingClientRect().bottom-(window.innerHeight-12);
if(u>0)f.style.top=(-10-u)+'px';
}
s.addEventListener('mouseenter',platzieren);
s.addEventListener('focusin',platzieren);
window.addEventListener('resize',function(){f.removeAttribute('style');});
});
});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
