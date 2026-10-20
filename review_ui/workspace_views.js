(()=>{'use strict';
const names=['showcase','assess','engineering'],tabs=names.map(n=>document.getElementById('tab'+n[0].toUpperCase()+n.slice(1)));
function open(name,focus=false){const index=names.indexOf(name);if(index<0)return;names.forEach((n,i)=>{document.getElementById(n+'View').hidden=i!==index;tabs[i].setAttribute('aria-selected',String(i===index));tabs[i].tabIndex=i===index?0:-1;});if(focus)tabs[index].focus();document.title='Supplier Risk Copilot · '+tabs[index].textContent;history.replaceState(null,'','#'+name);}
tabs.forEach((tab,i)=>{tab.onclick=()=>open(names[i]);tab.onkeydown=e=>{let next=i;if(e.key==='ArrowRight')next=(i+1)%3;else if(e.key==='ArrowLeft')next=(i+2)%3;else if(e.key==='Home')next=0;else if(e.key==='End')next=2;else return;e.preventDefault();open(names[next],true);};});
document.querySelectorAll('[data-open-view]').forEach(b=>b.onclick=()=>open(b.dataset.openView,true));
open(names.includes(location.hash.slice(1))?location.hash.slice(1):'showcase');
})();
