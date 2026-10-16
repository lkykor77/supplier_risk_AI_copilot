const $ = id => document.getElementById(id);
const labels = {met:'Met', partly_met:'Partly met', missing:'Missing', unknown:'Unknown'};
let run = null, selectedSupplier = null, editing = null;
function modelName(model) { return /^qwen\//i.test(model) ? 'Open-weight LLM' : model; }
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
    for(const item of catalog) { const option=node('option','',`${modelName(item.model)} · ${item.dataset} · ${item.count} assessments${item.context_mode==='selected-vault-notes'?' · vault rules':''}`); option.value=item.id; $('runSelect').append(option); }
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
    button.append(node('strong','',FrameworkView.supplierName(supplier.id)),node('small','',`${reviewed} / ${supplier.assessments.length} reviewed`));
    button.onclick=()=>{selectedSupplier=supplier.id;render();};
    button.setAttribute('aria-current',supplier.id===selectedSupplier?'true':'false'); $('suppliers').append(button);
  }
  const supplier=run.suppliers.find(s=>s.id===selectedSupplier);
  $('showKey').disabled=run.meta.dataset==='pdf';if($('showKey').disabled)$('showKey').checked=false;
  $('keyWarning').textContent=run.meta.dataset==='pdf'?'PDF assessments have no benchmark answer key':'Draft labels · not independently validated';
  $('supplierTitle').textContent=FrameworkView.supplierName(supplier.id)+' · questionnaire';
  const risk=supplier.risk||{ready:false,supplier_class:'normal',reviewed:supplier.assessments.filter(r=>r.review).length,total:supplier.assessments.length};
  RiskView.render($('riskResult'),risk);$('supplierClass').value=risk.supplier_class;
  $('classNotice').textContent=`Classification changes recorded: ${(run.classification_events||[]).filter(e=>e.supplier_id===supplier.id).length}.`;
  $('runMeta').textContent=`${modelName(run.meta.model)} · ${run.meta.dataset} · ${run.meta.context_mode==='selected-vault-notes'?'Selected Obsidian context':'Original assessment prompt'}`;
  $('reviewProgress').textContent=`${run.reviewed_count} / ${run.meta.count} reviewed`;
  $('progress').max=run.meta.count; $('progress').value=run.reviewed_count;
  $('cards').replaceChildren();
  const rows=supplier.assessments.filter(row=>!$('pendingOnly').checked||!row.review);
  for(const row of rows) $('cards').append(card(row));
  if(!rows.length)$('cards').append(node('div','empty','All assessments for this supplier have been reviewed.'));
  $('historyCount').textContent=run.events.length; $('history').replaceChildren();
  for(const event of [...run.events].reverse()) {
    const entry=node('div','event');
    entry.append(node('strong','',`${FrameworkView.supplierName(event.supplier_id)} · ${FrameworkView.label(event.requirement_id)} · ${event.after.action}`),
      node('div','',`${event.after.reviewer} · ${new Date(event.after.updated_at).toLocaleString()} · ${labels[event.after.status]}`));
    if(event.after.comment)entry.append(node('div','',event.after.comment)); $('history').append(entry);
  }
}
function card(row) {
  const article=node('article','card'), top=node('div','card-top'), title=node('div');
  const supplier=run.suppliers.find(s=>s.id===selectedSupplier);const q=FrameworkView.questions[row.requirement_id];
  title.append(node('div','requirement-id',FrameworkView.supplierName(selectedSupplier)+' · '+FrameworkView.label(row.requirement_id)+' of '+supplier.assessments.length),node('h3','',q?.question||row.description));
  top.append(title,node('span','pill '+row.ai.status,'Question result · '+labels[row.ai.status])); article.append(top,node('p','buyer-criterion','Assessment question: '+row.description));
  const columns=node('div','columns'), answer=node('div'), suggestion=node('div');
  answer.append(node('p','field-title','Supplier answer'),node('p','answer',row.answer||'No answer supplied.'));
  suggestion.append(node('p','field-title','AI evidence & explanation'),node('p','quote',row.ai.evidence_quote||'No evidence quote.'),node('p','reason',row.ai.reason));
  columns.append(answer,suggestion);article.append(columns);FrameworkView.render(article,row.requirement_id);
  if(row.review) {
    const review=node('div','decision');
    review.append(node('strong','',`Your decision · ${labels[row.review.status]} · ${row.review.action}`),
      node('p','',row.review.evidence_quote||'No evidence quote.'),node('p','',row.review.reason));
    if(row.review.comment)review.append(node('p','',`Review note: ${row.review.comment}`));article.append(review);
  }
  if(row.pdf_source){const source=node('div','answer-key');source.append(node('span','',`PDF evidence · page(s) ${row.pdf_source.pages.join(', ')||'not found'}${row.pdf_source.ocr_corrected?' · OCR wording corrected by analyst':''} · `));const link=node('a','','Open source PDF');link.href='/api/pdf?id='+encodeURIComponent(row.pdf_source.document_id)+'#page='+(row.pdf_source.pages[0]||1);link.target='_blank';link.rel='noopener';source.append(link);article.append(source);}
  if($('showKey').checked&&row.expected)article.append(node('div','answer-key',`Synthetic answer key: ${labels[row.expected]}. Treat this draft label as a learning reference, not verified ground truth.`));
  const actions=node('div','card-actions'), buttons=node('div');
  actions.append(node('span','review-state',row.review?`Reviewed by ${row.review.reviewer}`:'Awaiting your review'));
  if(!row.review) { const accept=node('button','primary','Accept AI suggestion'); accept.onclick=async()=>{accept.disabled=true;try{await save(row,row.ai,'');}finally{accept.disabled=false;}};buttons.append(accept); }
  const edit=node('button','secondary',row.review?'Edit your decision':'Correct assessment');edit.onclick=()=>openEditor(row);buttons.append(edit);
  actions.append(buttons);article.append(actions);return article;
}
function openEditor(row) {
  editing=row; $('editTitle').textContent=FrameworkView.supplierName(selectedSupplier)+' · '+FrameworkView.label(row.requirement_id);$('editRequirement').textContent=row.description;
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

let pdfDocument=null;
$('uploadPdf').onclick=()=>$('pdfFile').click();
$('pdfFile').onchange=async()=>{
  const file=$('pdfFile').files[0];if(!file)return;
  if(file.size>10*1024*1024){notice('Choose a PDF no larger than 10 MB.',true);return;}
  const started=Date.now();const progressTimer=setInterval(()=>{if($('uploadPdf').disabled)notice(`Processing locally · ${Math.round((Date.now()-started)/1000)} seconds elapsed. Extracting PDF/OCR and matching evidence; keep LM Studio running.`);},1000);
  $('uploadPdf').disabled=true;notice('Extracting PDF text and on-device OCR. The first run may build the local helper…');
  try{
    const encoded=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result.split(',')[1]);reader.onerror=reject;reader.readAsDataURL(file);});
    pdfDocument=await api('/api/pdf/upload',{filename:file.name,base64:encoded});
    notice('PDF extracted. The local Open Weight AI model is matching evidence to 20 questions. This can take several minutes…');
    const suggestions=await api('/api/pdf/suggest',{document_id:pdfDocument.id});
    const proposed=Object.fromEntries(suggestions.mappings.map(m=>[m.requirement_id,m]));
    $('pdfSummary').textContent=`${pdfDocument.filename} · ${pdfDocument.pages.length} page(s) · ${pdfDocument.native_engine} + ${pdfDocument.ocr_engine}`;
    $('pdfReviewer').value=$('reviewer').value;
    $('originalPdf').href='/api/pdf?id='+encodeURIComponent(pdfDocument.id);$('pdfPage').replaceChildren();
    for(const page of pdfDocument.pages){const option=node('option','',`Page ${page.page}`);option.value=page.page;$('pdfPage').append(option);}
    $('pdfMappings').replaceChildren();
    for(const requirement of pdfDocument.requirements){
      const field=node('div','mapping');field.dataset.requirementId=requirement.id;field.dataset.modes=JSON.stringify(proposed[requirement.id].modes);
      const draft=proposed[requirement.id];field.append(node('p','',draft.extraction_note));
      field.append(node('h3','',`${FrameworkView.label(requirement.id)} · ${requirement.description}`));if(requirement.hecvat_reference)field.append(node('small','',`Related HECVAT Lite topic: ${requirement.hecvat_reference}`));
      const answerLabel=node('label','','Supplier answer'),answer=node('textarea');answer.value=draft.answer;answer.rows=3;answer.className='mapped-answer';answer.maxLength=16000;answerLabel.append(answer);field.append(answerLabel);
      const copy=node('button','secondary','Copy selected answer');copy.type='button';copy.onclick=()=>{const box=$('pageText');const text=box.value.slice(box.selectionStart,box.selectionEnd);if(!text.trim()){ $('pdfError').textContent='Select answer text in the source-page box first.';return;}answer.value=text;field.querySelector('.mapped-pages').value=$('pdfPage').value;field.dataset.modes=JSON.stringify({[$('pdfPage').value]:$('pdfMode').value});$('pdfError').textContent='';};field.append(copy);
      const pagesLabel=node('label','','Source pages (for example 1, 2)'),pages=node('input');pages.className='mapped-pages';pages.value=draft.pages.join(', ');pages.placeholder='Leave blank when not found';pagesLabel.append(pages);field.append(pagesLabel);
      const correctionLabel=node('label','','OCR correction note (only if you fix extracted wording)'),correction=node('input');correction.className='mapped-correction';correction.value=draft.correction_note;correction.placeholder='None — wording unchanged';correction.maxLength=2000;correctionLabel.append(correction);field.append(correctionLabel);const absent=node('button','secondary','Mark as not found');absent.type='button';absent.onclick=()=>{answer.value='';pages.value='';correction.value='';field.dataset.modes='{}';};field.append(absent);$('pdfMappings').append(field);
    }
    $('confirmPdf').checked=false;$('pdfVault').checked=false;$('pdfError').textContent='';showPdfPage();$('pdfDialog').showModal();notice('Answers and pages proposed automatically. Review and approve; no page is required for a blank answer.');
  }catch(error){notice(error.message,true);}finally{clearInterval(progressTimer);$('uploadPdf').disabled=false;$('pdfFile').value='';}
};
function showPdfPage(){const page=pdfDocument.pages.find(p=>p.page===Number($('pdfPage').value));$('pdfMode').value=page.mode;showPdfText();}
function showPdfText(){const page=pdfDocument.pages.find(p=>p.page===Number($('pdfPage').value));page.mode=$('pdfMode').value;$('pageText').value=page[page.mode+'_text'];$('pageWarning').textContent=page.warning|| (page.mode==='ocr'?'OCR text can contain errors. Check it against the original page.':'PDF text order can differ from the visual layout. Check tables and embedded images; switch to OCR when needed.');}
$('pdfPage').onchange=showPdfPage;$('pdfMode').onchange=showPdfText;
$('closePdf').onclick=()=>$('pdfDialog').close();
$('assessPdf').onclick=async()=>{
  if(!$('pdfReviewer').value.trim()){$('pdfError').textContent='Enter your name or initials before confirming answers.';return;}
  $('reviewer').value=$('pdfReviewer').value;localStorage.setItem('reviewer',$('reviewer').value);
  if(!$('confirmPdf').checked){$('pdfError').textContent='Check the confirmation box after inspecting the answers against the PDF.';return;}
  $('assessPdf').disabled=true;$('closePdf').disabled=true;$('pdfError').textContent='Saving the confirmed mapping, then running the local model. This may take a minute…';
  try{
    const modes=Object.fromEntries(pdfDocument.pages.map(p=>[String(p.page),p.mode]));
    const mappings=[...$('pdfMappings').children].map(field=>({requirement_id:field.dataset.requirementId,
      answer:field.querySelector('.mapped-answer').value,pages:field.querySelector('.mapped-pages').value.split(',').map(s=>s.trim()).filter(Boolean).map(Number),modes:{...modes,...JSON.parse(field.dataset.modes)},
      correction_note:field.querySelector('.mapped-correction').value}));
    const confirmed=await api('/api/pdf/confirm',{document_id:pdfDocument.id,confirmed:true,reviewer:$('reviewer').value,mappings});
    const assessed=await api('/api/pdf/assess',{...confirmed,with_vault:$('pdfVault').checked});
    $('pdfDialog').close();await refresh();$('runSelect').value=assessed.report_sha256;await loadRun();notice('PDF assessment ready. Inspect the page references and review every AI suggestion.');
  }catch(error){$('pdfError').textContent=error.message;}finally{$('assessPdf').disabled=false;$('closePdf').disabled=false;}
};

$('supplierClass').onchange=async()=>{if(!run)return;const input=$('supplierClass');input.disabled=true;try{run=await api('/api/supplier-class',{run_id:run.meta.id,revision:run.revision,supplier_id:selectedSupplier,reviewer:$('reviewer').value,supplier_class:input.value});render();notice('Supplier class saved with revision history.');}catch(error){render();$('classNotice').textContent=error.message;}finally{input.disabled=false;}};
