"""Fixed questionnaire-gap scoring, with explicit supplier criticality."""
VERSION = "questionnaire-gap-v1"
PENALTIES = {"met": 0, "partly_met": 0.5, "missing": 1, "unknown": 1}


def summarize_risk(rows, supplier_class="normal"):
    if supplier_class not in {"normal", "critical"}:
        raise ValueError("Choose normal or critical supplier.")
    reviewed = sum(row.get("review") is not None for row in rows)
    result = {"ready": False, "version": VERSION, "supplier_class": supplier_class,
              "reviewed": reviewed, "total": len(rows)}
    if not rows or reviewed != len(rows):
        return result
    known, unresolved, breakdown, findings = 0, 0, [], []
    share = 100 / len(rows)
    for row in rows:
        rid, status = row["requirement_id"], row["review"]["status"]
        if status not in PENALTIES:
            raise ValueError("Invalid reviewed status for scoring.")
        points = share * PENALTIES[status]
        if status == "unknown": unresolved += points
        else: known += points
        if status != "met": findings.append({"requirement_id": rid, "status": status})
        breakdown.append({"requirement_id": rid, "status": status, "weight_percent": round(share, 2),
                          "factor": PENALTIES[status], "points": round(points, 2)})
    result.update(ready=True, score=round(known + unresolved, 2),
                  confirmed_gap_points=round(known, 2), unresolved_evidence_points=round(unresolved, 2),
                  unknown_count=sum(r["status"] == "unknown" for r in breakdown),
                  findings=findings, enhanced_review=supplier_class == "critical" and bool(findings),
                  breakdown=breakdown)
    return result
