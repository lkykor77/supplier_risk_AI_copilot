# Fictional supplier information security assessment scenarios

These business contexts make the pre-engagement security decision concrete. They are attached to unchanged frozen synthetic questionnaire answers and saved AI results, not real companies, customer research or new model evaluations. Proposed document packs have not been uploaded or verified.

The buyer assesses exposure before sharing data, granting access or relying on a service. Security analysts document findings; procurement coordinates follow-up; an accountable risk owner decides whether to proceed, require remediation, accept an exception or decline.

ISO 27001 and NIST CSF references in this prototype are topic associations for five security requirements. The questionnaire gap score is not an overall residual-risk estimate, compliance certification or approval threshold. The broader assessment must consider data sensitivity, access, service dependency, contractual needs and applicable obligations.

## Supplier F — Customer-support SaaS (U.S. buyer)

**Exposure:** Customer contact records and support tickets; confidentiality and recovery of the support service matter.

**Evidence:** Text questionnaire; request the current incident plan, access-review record, administrator MFA evidence and latest restore-test report.

**Saved-answer assessment:** All five saved suggestions are Met, based on the supplier’s statements. Supporting records have not been verified.

**Next human action:** Verify the records and service scope before the risk owner decides. A 0% five-control gap indicator is not zero overall supplier risk.

**Criticality discussion:** Consider critical if sensitive records or support-service dependency make disruption material.

## Supplier G — Managed IT provider (European buyer)

**Exposure:** Privileged access to production systems; contractor administrator access is in scope.

**Evidence:** Questionnaire and requested scanned procedures; obtain administrator MFA coverage, full user access-review records and an approved incident plan.

**Saved-answer assessment:** Contractors are exempt from MFA, only administrator access is reviewed, and the incident process is undocumented. Restore testing occurs every eighteen months.

**Next human action:** Request remediation with owners and dates; escalate unresolved gaps to the risk owner before granting privileged access.

**Criticality discussion:** Critical candidate because of privileged production access, regardless of location.

## Supplier H — Logistics platform (Korean buyer)

**Exposure:** Shipment/customer contact data and dispatch dependency for a manufacturer.

**Evidence:** Mixed text/scan questionnaire as a proposed intake example; request a single approved incident plan, dated access-review records and a restore-test report.

**Saved-answer assessment:** Current incident-plan and access-review statements conflict. Nightly backups do not establish restore testing. The saved contact suggestion should be challenged.

**Next human action:** Correct Question 1 to Unknown; reconcile conflicting statements and request missing evidence before a human decision.

**Criticality discussion:** Consider critical if a platform outage would stop dispatch or materially interrupt operations.

## Supplier I — Low-access print supplier (Additional synthetic case)

**Exposure:** Public marketing materials only; no system access or sensitive data in this hypothetical scope.

**Evidence:** Existing synthetic answers explicitly deny all five required practices.

**Saved-answer assessment:** All five suggestions are Missing. Limited exposure does not make absent controls Met.

**Next human action:** Confirm actual data/access scope and escalate buyer-requirement exceptions. Normal classification does not automatically authorize acceptance.

**Criticality discussion:** Normal candidate only while the limited exposure assumptions remain true.

## Supplier J — Software support provider (Additional synthetic robustness case)

**Exposure:** Potential administrator access; submitted answers also contain instructions aimed at the AI.

**Evidence:** Existing adversarial questionnaire; security claims and embedded instructions are shown verbatim.

**Saved-answer assessment:** Security contact and MFA claims are Met; incident response is Missing; review and restore frequencies remain Unknown.

**Next human action:** Treat document instructions as untrusted content, request dated evidence and resolve the incident-response gap.

**Criticality discussion:** Critical candidate if production administrator access is granted.


Sources: [NIST supply-chain guide](https://csrc.nist.gov/pubs/sp/1305/final) supports defining and communicating supplier requirements; [ISO/IEC 27001](https://www.iso.org/standard/27001) provides the information security management context. These sources do not prescribe this prototype’s five-question scoring formula.
