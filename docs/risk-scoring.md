# Weighted questionnaire risk indicator

## Simple workflow

Review every assessment for the selected supplier. The score appears only when all requirements have an explicit human decision. Choose **Normal supplier** (the default) or **Critical supplier**. No custom weighting form is needed.

Classify a supplier as critical based on the actual relationship: important service dependency, sensitive data, privileged access or substantial harm from supplier failure. This classification is a human choice, not an inference from questionnaire wording. Changes in the local app retain reviewer identity, before/after history, and revision checks. Public demo choices stay in browser session storage.

## Fixed prototype formula

All current requirements have equal importance (20% each for the five-control questionnaire). Status factors are:

| Human decision | Factor | Interpretation |
| --- | --- | --- |
| Met | 0 | No questionnaire gap stated |
| Partly met | 0.5 | Explicit partial gap |
| Missing | 1 | Explicitly absent practice |
| Unknown | 1 | Conservative unresolved-evidence penalty; not proof of absence |

Score = **100 × sum(requirement weight × status factor)**.

The interface separates confirmed control-gap points from unresolved-evidence points and displays a per-requirement contribution table. Higher scores mean more gaps or unresolved evidence. The number is not a probability, measured financial loss, or a complete residual-risk rating. A score of zero does not prove a secure supplier.

Normal and critical suppliers use the same numerical scale so equal questionnaire answers remain comparable. The prototype does not invent a criticality multiplier. **Critical suppliers receive an enhanced-review flag for any partial, missing or unknown answer.** Normal suppliers receive an ordinary follow-up message. Both still need a human onboarding decision, and critical relationships require proportionate due diligence beyond this questionnaire.

### Example

Five equal-weight human decisions: met, partly met, missing, unknown, met:

- Confirmed gaps: 10 + 20 = **30 points**.
- Unresolved evidence: **20 points**, representing one unknown answer.
- Total questionnaire indicator: **50 / 100**.
- Critical supplier: enhanced-review flag naming the three non-met requirements.

These factors and flags are explicit project choices. They have not been validated as an organization-approved risk policy.

## Governance rationale and limits

[NIST SP 800-30 Rev. 1, Task 1-5](https://csrc.nist.gov/pubs/sp/800/30/r1/final) calls for organization-specific risk models, documented assumptions and combining rules; it does not prescribe universal weights for these five controls. [NIST SP 800-161 Rev. 1 Update 1](https://csrc.nist.gov/pubs/sp/800/161/r1/upd1/final) considers supplier criticality and includes impact/likelihood assessment examples. [ISO/IEC 27005](https://www.iso.org/standard/80585.html) provides information-security risk management guidance.

The fixed factors, equal weights and enhanced-review flag are **not mandated or endorsed numerical values from ISO or NIST**. The design follows the general idea of transparent assessment and proportionate attention to critical suppliers, while keeping the portfolio workflow simple.

A comprehensive supplier risk assessment needs validated framework mappings, threat scenarios, business impact, likelihood, actual control effectiveness, evidence confidence, compensating controls and the organization's risk acceptance criteria. Those are future work. This prototype does not impose low/medium/high thresholds or automatically approve a supplier.
