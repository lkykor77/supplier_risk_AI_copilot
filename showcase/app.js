'use strict';
const $=id=>document.getElementById(id), labels={met:'Met',partly_met:'Partly met',missing:'Missing',unknown:'Unknown'};
const storageKey='supplier-risk-public-demo-v1';
let scenarios=[],data,selected,editing,decisions={},history=[],supplierClasses={};
function node(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;}
function persist(){try{sessionStorage.setItem(storageKey,JSON.stringify({decisions,history,supplierClasses}));}catch{}}
function key(id){return selected+':'+id;}
function render(){
 const supplier=data.suppliers.find(s=>s.id===selected);$('cards').replaceChildren();$('supplierHeading').textContent=FrameworkView.supplierName(selected)+' · questionnaire';$('supplierAnswerCount').textContent=`These ${supplier.assessments.length} answers were provided by ${FrameworkView.supplierName(selected)}. Each card is one question, not another supplier.`;
 const context=scenarios.find(s=>s.supplier===selected);$("supplierContext").replaceChildren();
 if(context){const box=$("supplierContext");box.append(node("strong","",context.region+" · "+context.title));for(const [label,value] of [["Exposure",context.exposure],["Evidence to request",context.evidence],["Assessment focus",context.finding],["Human follow-up",context.action],["Classification to consider",context.criticality]])box.append(node("p","",label+": "+value));box.append(node("p","quiet","Fictional business context; proposed evidence packs are not uploaded records. Choose the supplier class below after considering exposure."));}
 let count=0;
 for(const row of supplier.assessments){
  const req=data.requirements.find(r=>r.id===row.requirement_id),answer=supplier.answers[req.question_id],review=decisions[key(req.id)];if(review)count++;
  const card=node('article','card'),head=node('div','card-head'),title=node('div');
  const q=FrameworkView.questions[req.id];title.append(node('div','requirement-id',FrameworkView.supplierName(selected)+' · '+FrameworkView.label(req.id)+' of '+supplier.assessments.length),node('h3','',q?.question||req.description));head.append(title,node('span','status '+row.status,'Buyer requirement · '+labels[row.status]));card.append(head,node('p','buyer-criterion','Buyer requirement: '+req.description));
  const columns=node('div','columns'),source=node('div'),result=node('div');source.append(node('p','field-title','SUPPLIER ANSWER'),node('p','answer',answer||'No answer supplied.'));result.append(node('p','field-title','SAVED AI EVIDENCE & EXPLANATION'),node('p','quote',row.evidence_quote||'No evidence quote.'),node('p','reason',row.reason));columns.append(source,result);card.append(columns);FrameworkView.render(card,req.id);
  if(review){const box=node('div','decision');box.append(node('strong','',`Your demo decision · ${labels[review.status]} · ${review.action}`),node('p','',review.reason));if(review.comment)box.append(node('p','',`Change note: ${review.comment}`));card.append(box);}
  if($('showKey').checked)card.append(node('div','rubric',`Draft rubric label: ${labels[row.expected]}. Keyword baseline: ${labels[row.baseline_status]}. This is a synthetic learning reference.`));
  const actions=node('div','card-actions'),buttons=node('div');actions.append(node('span','',review?'Reviewed in this demo':'Awaiting demo review'));
  if(!review){const accept=node('button','button primary','Accept suggestion');accept.onclick=()=>save(row,{status:row.status,evidence_quote:row.evidence_quote,reason:row.reason,comment:'',action:'accepted'});buttons.append(accept);}
  const edit=node('button','button outlined',review?'Edit decision':'Correct assessment');edit.onclick=()=>openEditor(row,req,review);buttons.append(edit);actions.append(buttons);card.append(actions);$('cards').append(card);
 }
 const riskRows=supplier.assessments.map(row=>({...row,description:data.requirements.find(r=>r.id===row.requirement_id).description,review:decisions[key(row.requirement_id)]}));RiskView.render($('riskResult'),RiskView.calculate(riskRows,supplierClasses[selected]||'normal'));$('supplierClass').value=supplierClasses[selected]||'normal';
 $('progress').textContent=`${count} / 5 reviewed`;$('progressBar').value=count;$('historyCount').textContent=history.length;$('history').replaceChildren();
 for(const event of [...history].reverse()){const e=node('div','event');e.append(node('strong','',`${FrameworkView.supplierName(event.supplier)} · ${FrameworkView.label(event.requirement)} · ${event.decision.action} → ${labels[event.decision.status]}`),node('p','',event.decision.comment||'Accepted the saved suggestion.'));$('history').append(e);}
}
function save(row,decision){decisions[key(row.requirement_id)]=decision;history.push({supplier:selected,requirement:row.requirement_id,decision});persist();render();$('notice').textContent='Demo decision saved in this browser session. The original model result is unchanged.';}
function openEditor(row,req,review){editing={row,req,supplier:selected};const draft=review||row;$('editTitle').textContent=FrameworkView.supplierName(selected)+' · '+FrameworkView.label(req.id);$('editRequirement').textContent=req.description;$('editStatus').value=draft.status;$('editQuote').value=draft.evidence_quote;$('editReason').value=draft.reason;$('editComment').value=review?.comment||'';$('editError').textContent='';$('editor').showModal();}
function showFailure(){if(!data)return;selected='evaluation-h';$('supplier').value=selected;$('showKey').checked=true;render();$('notice').textContent='Supplier H, Question 1 is the saved model error: unspecified contact ownership was labeled Missing. The draft rubric expects Unknown.';$('demo').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});}
$('failureHero').onclick=showFailure;$('showError').onclick=showFailure;
$('supplier').onchange=()=>{selected=$('supplier').value;$('notice').textContent='';render();};$('showKey').onchange=()=>data&&render();
$('closeEditor').onclick=()=>$('editor').close();
$('editForm').onsubmit=event=>{event.preventDefault();if(editing.supplier!==selected)return;
 const quote=$('editQuote').value.trim(),reason=$('editReason').value.trim(),comment=$('editComment').value.trim();const answer=data.suppliers.find(s=>s.id===selected).answers[editing.req.question_id];
 if(!reason||!comment){$('editError').textContent='Enter a reason and change note.';return;}
 if(quote&&!answer.includes(quote)){$('editError').textContent='Copy a verbatim quote from this supplier answer, or leave the quote blank.';return;}
 save(editing.row,{status:$('editStatus').value,evidence_quote:quote,reason,comment,action:'corrected'});$('editor').close();
};
$('reset').onclick=()=>{decisions={};history=[];supplierClasses={};persist();if(data)render();$('notice').textContent='Demo decisions cleared. Saved AI results are unchanged.';};
(async()=>{try{const response=await fetch('demo-data.json');if(!response.ok)throw Error('Unable to load examples.');data=await response.json();const scenarioResponse=await fetch('scenario-data.json');if(!scenarioResponse.ok)throw Error('Unable to load scenario context.');scenarios=await scenarioResponse.json();for(const context of scenarios.slice(0,3)){const card=node('article');card.append(node('p','eyebrow',context.region+' · FICTIONAL'),node('h3','',context.title),node('p','',context.exposure),node('p','',context.finding));const button=node('button','button outlined','Review Supplier '+context.supplier.slice(-1).toUpperCase()+' →');button.onclick=()=>{selected=context.supplier;$('supplier').value=selected;render();$('notice').textContent='Scenario selected. Review the saved answers and choose supplier criticality based on exposure.';$('demo').scrollIntoView({behavior:'auto'});};card.append(button);$('scenarioCards').append(card);}try{const saved=JSON.parse(sessionStorage.getItem(storageKey));if(saved&&typeof saved.decisions==='object'&&Array.isArray(saved.history)){decisions=saved.decisions;history=saved.history;supplierClasses=saved.supplierClasses||{};}}catch{}
 const names={'evaluation-f':'Fictional Supplier F · Customer-support SaaS','evaluation-g':'Fictional Supplier G · Managed IT provider','evaluation-h':'Fictional Supplier H · Logistics / model error','evaluation-i':'Fictional Supplier I · Low-access print supplier','evaluation-j':'Fictional Supplier J · Software support / injected instructions'};
 for(const supplier of data.suppliers){const option=node('option','',names[supplier.id]||supplier.id);option.value=supplier.id;$('supplier').append(option);}selected=data.suppliers[0].id;render();
 }catch(error){$('cards').replaceChildren(node('p','',error.message+' Open the GitHub repository for saved reports.'));}})();

$('supplierClass').onchange=()=>{if(!data)return;supplierClasses[selected]=$('supplierClass').value;persist();render();$('notice').textContent='Demo supplier class saved in this browser session.';};
