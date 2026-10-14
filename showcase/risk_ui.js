/* Fixed prototype scoring shared by the local app and public demo. */
(function(global){
'use strict';
const labels={met:'Met',partly_met:'Partly met',missing:'Missing',unknown:'Unknown'};
function calculate(rows,supplierClass='normal'){
 const result={ready:false,version:'questionnaire-gap-v1',supplier_class:supplierClass,reviewed:rows.filter(r=>r.review).length,total:rows.length};
 if(!rows.length||result.reviewed!==rows.length)return result;
 const share=100/rows.length;let known=0,unresolved=0;const breakdown=[],findings=[];
 for(const row of rows){const status=row.review.status,factor={met:0,partly_met:.5,missing:1,unknown:1}[status],points=share*factor;if(status==='unknown')unresolved+=points;else known+=points;if(status!=='met')findings.push({requirement_id:row.requirement_id,status});breakdown.push({requirement_id:row.requirement_id,status,weight_percent:share,factor,points});}
 return {...result,ready:true,score:known+unresolved,confirmed_gap_points:known,unresolved_evidence_points:unresolved,unknown_count:breakdown.filter(r=>r.status==='unknown').length,findings,enhanced_review:supplierClass==='critical'&&findings.length>0,breakdown};
}
function element(tag,text){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;return e;}
function render(target,result){target.replaceChildren();target.append(element('h3','Weighted questionnaire risk indicator'));target.append(element('p',result.supplier_class==='critical'?'Critical supplier · greater business consequence; enhanced due diligence':'Normal supplier · standard due diligence (default classification)'));
 if(!result.ready){target.append(element('p',`${result.reviewed} / ${result.total} human decisions recorded. Complete every review to show the score.`));return;}
 target.append(element('strong',`${result.score.toFixed(1)} / 100`));
 target.append(element('p',`Confirmed control gaps: ${result.confirmed_gap_points.toFixed(1)} points. Unresolved evidence: ${result.unresolved_evidence_points.toFixed(1)} points (${result.unknown_count} unknown answers). Unknown is a conservative evidence penalty, not a confirmed missing control.`));
 target.append(element('p',result.enhanced_review?'Enhanced review required for critical supplier: '+result.findings.map(r=>(global.FrameworkView?.label(r.requirement_id)||r.requirement_id)+' ('+labels[r.status]+')').join(', '):result.findings.length?'Follow up on non-met answers before the human supplier-security decision.':'No questionnaire gap was recorded. This does not automatically approve the supplier.'));
 const details=element('details'),summary=element('summary','Show scoring contributions');details.append(summary);const table=element('table'),head=element('tr');for(const text of ['Requirement','Human decision','Weight','Factor','Points'])head.append(element('th',text));table.append(head);for(const row of result.breakdown){const tr=element('tr');for(const text of [global.FrameworkView?.label(row.requirement_id)||row.requirement_id,labels[row.status],row.weight_percent.toFixed(1)+'%',String(row.factor),row.points.toFixed(1)])tr.append(element('td',text));table.append(tr);}details.append(table);target.append(details);
 target.append(element('p','Fixed prototype rule: met = 0, partly met = 0.5, missing = 1, unknown = 1. Equal requirement weights. Higher means more gaps or unresolved evidence, not breach probability. Normal and critical suppliers use the same score; criticality changes the follow-up flag. ISO/NIST do not prescribe these numeric values. Impact, likelihood and actual control effectiveness require further assessment.'));
}
global.RiskView={calculate,render};if(typeof module!=='undefined')module.exports=global.RiskView;
})(typeof window==='undefined'?globalThis:window);
