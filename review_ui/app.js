const $ = id => document.getElementById(id);
const labels = {met:'Met', partly_met:'Partly met', missing:'Missing', unknown:'Unknown'};
let run = null, selectedSupplier = null, editing = null;
function node(tag, cls, text) { const e=document.createElement(tag); if(cls)e.className=cls; if(text!==undefined)e.textContent=text; return e; }
function notice(text, error=false) { $('notice').textContent=text; $('notice').className=error?'error':''; }
async function api(url, payload) {
  const options=payload?{method:'POST',headers:{'Content-Type':'application/json','X-Review-App':'1'},body:JSON.stringify(payload)}:{};
  const response=await fetch(url,options); const data=await response.json();
  if(!response.ok)throw new Error(data.error||'Request failed.'); return data;
}
async function refresh() {
  try {
    const catalog=await api('/api/runs'), previous=$('runSelect').value;
    $('runSelect').replaceChildren();
    for(const item of catalog) { const option=node('option','',`${item.model} · ${item.dataset} · ${item.count} assessments${item.context_mode==='selected-vault-notes'?' · vault rules':''}`); option.value=item.id; $('runSelect').append(option); }
    if(!catalog.length){run=null; $('cards').replaceChildren(node('div','empty','No completed reports yet. Run an assessor, then refresh.')); return;}
    if(catalog.some(item=>item.id===previous))$('runSelect').value=previous;
    await loadRun();
  } catch(error){notice(error.message,true);}
}
async function loadRun() {
  run=await api('/api/run?id='+encodeURIComponent($('runSelect').value));
  if(!run.suppliers.some(s=>s.id===selectedSupplier))selectedSupplier=run.suppliers[0].id;
  render(); notice('Saved model output loaded. Each assessment needs your explicit review.');
}
function render() {
  if(!run)return;
  $('supplierCount').textContent=run.suppliers.length; $('suppliers').replaceChildren();
  for(const supplier of run.suppliers) {
    const reviewed=supplier.assessments.filter(r=>r.review).length;
    const button=node('button','supplier'+(supplier.id===selectedSupplier?' active':''));
    button.append(node('strong','',supplier.id),node('small','',`${reviewed} / ${supplier.assessments.length} reviewed`));
    button.onclick=()=>{selectedSupplier=supplier.id;render();};
    button.setAttribute('aria-current',supplier.id===selectedSupplier?'true':'false'); $('suppliers').append(button);
  }
  const supplier=run.suppliers.find(s=>s.id===selectedSupplier);
  $('supplierTitle').textContent=supplier.id;
  $('runMeta').textContent=`${run.meta.model} · ${run.meta.dataset} · ${run.meta.context_mode==='selected-vault-notes'?'Selected Obsidian context':'Original assessment prompt'}`;
  $('reviewProgress').textContent=`${run.reviewed_count} / ${run.meta.count} reviewed`;
  $('progress').max=run.meta.count; $('progress').value=run.reviewed_count;
  $('cards').replaceChildren();
  const rows=supplier.assessments.filter(row=>!$('pendingOnly').checked||!row.review);
  for(const row of rows) $('cards').append(card(row));
  if(!rows.length)$('cards').append(node('div','empty','All assessments for this supplier have been reviewed.'));
  $('historyCount').textContent=run.events.length; $('history').replaceChildren();
  for(const event of [...run.events].reverse()) {
    const entry=node('div','event');
    entry.append(node('strong','',`${event.supplier_id} · ${event.requirement_id} · ${event.after.action}`),
      node('div','',`${event.after.reviewer} · ${new Date(event.after.updated_at).toLocaleString()} · ${labels[event.after.status]}`));
    if(event.after.comment)entry.append(node('div','',event.after.comment)); $('history').append(entry);
  }
}
function card(row) {
  const article=node('article','card'), top=node('div','card-top'), title=node('div');
  title.append(node('div','requirement-id',row.requirement_id),node('h3','',row.description));
  top.append(title,node('span','pill '+row.ai.status,'AI · '+labels[row.ai.status])); article.append(top);
  const columns=node('div','columns'), answer=node('div'), suggestion=node('div');
  answer.append(node('p','field-title','Supplier answer'),node('p','answer',row.answer||'No answer supplied.'));
  suggestion.append(node('p','field-title','AI evidence & explanation'),node('p','quote',row.ai.evidence_quote||'No evidence quote.'),node('p','reason',row.ai.reason));
  columns.append(answer,suggestion);article.append(columns);
  if(row.review) {
    const review=node('div','decision');
    review.append(node('strong','',`Your decision · ${labels[row.review.status]} · ${row.review.action}`),
      node('p','',row.review.evidence_quote||'No evidence quote.'),node('p','',row.review.reason));
    if(row.review.comment)review.append(node('p','',`Review note: ${row.review.comment}`));article.append(review);
  }
  if($('showKey').checked)article.append(node('div','answer-key',`Synthetic answer key: ${labels[row.expected]}. Treat this draft label as a learning reference, not verified ground truth.`));
  const actions=node('div','card-actions'), buttons=node('div');
  actions.append(node('span','review-state',row.review?`Reviewed by ${row.review.reviewer}`:'Awaiting your review'));
  if(!row.review) { const accept=node('button','primary','Accept AI suggestion'); accept.onclick=async()=>{accept.disabled=true;try{await save(row,row.ai,'');}finally{accept.disabled=false;}};buttons.append(accept); }
  const edit=node('button','secondary',row.review?'Edit your decision':'Correct assessment');edit.onclick=()=>openEditor(row);buttons.append(edit);
  actions.append(buttons);article.append(actions);return article;
}
function openEditor(row) {
  editing=row; $('editTitle').textContent=row.requirement_id+' · Review assessment';$('editRequirement').textContent=row.description;
  fillDraft(row.review||row.ai);$('editComment').value=row.review?.comment||'';$('editError').textContent='';$('editor').showModal();
}
function fillDraft(source){$('editStatus').value=source.status;$('editQuote').value=source.evidence_quote;$('editReason').value=source.reason;}
async function save(row,decision,comment) {
  const reviewer=$('reviewer').value.trim();
  if(!reviewer){notice('Enter your name or initials before saving a decision.',true);$('reviewer').focus();return false;}
  try {
    run=await api('/api/review',{run_id:run.meta.id,revision:run.revision,supplier_id:selectedSupplier,
      requirement_id:row.requirement_id,reviewer,comment,...decision});
    render();notice('Review saved locally. The original AI assessment is preserved.');return true;
  }catch(error){notice(error.message,true);if($('editor').open)$('editError').textContent=error.message;return false;}
}
$('editForm').onsubmit=async event=>{event.preventDefault();const submit=event.submitter;submit.disabled=true;try{
  if(await save(editing,{status:$('editStatus').value,evidence_quote:$('editQuote').value,reason:$('editReason').value},$('editComment').value))$('editor').close();
}finally{submit.disabled=false;}};
$('resetDraft').onclick=()=>{fillDraft(editing.ai);$('editComment').value='';};
$('closeEditor').onclick=()=>$('editor').close();
$('refresh').onclick=refresh;
$('runSelect').onchange=()=>loadRun().catch(error=>notice(error.message,true));
$('pendingOnly').onchange=render;$('showKey').onchange=render;
$('reviewer').value=localStorage.getItem('reviewer')||'';
$('reviewer').oninput=()=>localStorage.setItem('reviewer',$('reviewer').value);
refresh();
