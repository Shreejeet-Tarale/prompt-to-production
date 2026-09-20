# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify one complaint row into fixed category + priority + reason + flag.
    input: dict with complaint_id (str) and description (str, may be null/empty).
    output: dict with complaint_id, category (one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), priority (Urgent/Standard/Low), reason (one sentence quoting description words), flag (NEEDS_REVIEW or blank).
    error_handling: On null/empty/whitespace description return category Other, priority Standard, reason stating description missing, flag NEEDS_REVIEW. Never raise. Matching is case-insensitive substring on lowercased description; severity check runs before priority assignment; multi-category matches follow agents.md precedence and set NEEDS_REVIEW when flood+drain both match or result is Other.

  - name: batch_classify
    description: Read input CSV, apply classify_complaint per row, write results CSV.
    input: input_path (CSV with complaint_id, description columns among others), output_path (CSV to write).
    output: CSV with header complaint_id,category,priority,reason,flag, one row per input row, written even if some rows are malformed.
    error_handling: Missing file raises FileNotFoundError with path; bad/missing description per-row degrades to Other/NEEDS_REVIEW instead of crashing; missing complaint_id falls back to row number; always closes files and produces output header even on empty input.
