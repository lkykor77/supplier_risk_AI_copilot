/* Presentation-only topic references; model labels still assess the buyer rubric. */
(function(global){
'use strict';
const iso='https://www.iso.org/standard/27001';
const nist='https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf';
const questions={
 'BUYER-01':{number:1,question:'Who is your security contact?',iso:'A.5.2 · Security roles',nist:'GV.RR-02 · Cybersecurity responsibilities',page:22,scope:'A named contact supports one part of role assignment. It does not establish all responsibilities, authority, or enforcement.'},
 'BUYER-02':{number:2,question:'Do you have a documented incident response plan?',iso:'A.5.24 · Incident readiness',nist:'ID.IM-04 · Incident-response planning',page:24,scope:'This answer addresses documented planning. Communication, maintenance, improvement, and operational readiness need additional evidence.'},
 'BUYER-03':{number:3,question:'How often do you review access for all users?',iso:'A.5.18 · Access rights',nist:'PR.AA-05 · Access authorization and review',page:25,scope:'At least annually is this buyer’s threshold. The related controls cover broader access management; the annual interval is not a universal ISO/NIST rule.'},
 'BUYER-04':{number:4,question:'Is MFA required for every administrator account?',iso:'A.8.5 · Authentication safeguards',nist:'PR.AA-03 · Authentication',page:24,scope:'MFA for every administrator is this buyer’s requirement. Authentication outcomes are broader and depend on the organization’s risk-based policy.'},
 'BUYER-05':{number:5,question:'How often do you test restoring backups?',iso:'A.8.13 · Backup maintenance and testing',nist:'PR.DS-11 · Backup protection and testing',page:25,scope:'At least annually is this buyer’s restore-test threshold. Backup creation, protection, maintenance, recovery scope, and actual test evidence need further review.'}
};
function supplierName(id){const match=/^(evaluation|fictional)-([a-z])$/.exec(id);return match?'Fictional Supplier '+match[2].toUpperCase():id.startsWith('pdf-')?'Uploaded Supplier · '+id.slice(4):id;}
function label(id){return questions[id]?'Question '+questions[id].number:id;}
function node(tag,text){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;return e;}
function render(target,id){const q=questions[id];if(!q)return;const box=node('section');box.className='framework-reference';box.append(node('strong','Related framework criteria · topic alignment'));
 const links=node('p'),isoLink=node('a','ISO/IEC 27001:2022 '+q.iso),nistLink=node('a','NIST CSF 2.0 '+q.nist);isoLink.href=iso;nistLink.href=nist+'#page='+q.page;for(const link of [isoLink,nistLink]){link.target='_blank';link.rel='noopener';}links.append(isoLink,node('span',' · '),nistLink);box.append(links,node('p',q.scope),node('p','The result above evaluates the buyer requirement from this supplier’s answer. Full framework conformity is not assessed.'));target.append(box);}
global.FrameworkView={questions,supplierName,label,render};if(typeof module!=='undefined')module.exports=global.FrameworkView;
})(typeof window==='undefined'?globalThis:window);
