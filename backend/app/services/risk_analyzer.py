from app.services.query_service import run_query
from datetime import datetime
from app.db.mongodb import get_database

SECURITY_QUESTIONS = [
  {
    "id": "secrets",
    "category": "Secrets & Credentials",
    "question": "Are there any hardcoded API keys, passwords, tokens, or secrets in the code? Look for string literals that resemble credentials.",
    "weight": 20
  },
  {
    "id": "injection",
    "category": "Injection Vulnerabilities",
    "question": "Are there SQL queries, shell commands, or eval() calls that use unsanitized user input directly?",
    "weight": 20
  },
  {
    "id": "auth",
    "category": "Authentication & Authorization",
    "question": "Are there missing authentication checks, unprotected endpoints, or broken access control patterns?",
    "weight": 15
  },
  {
    "id": "dependencies",
    "category": "Dependency Security",
    "question": "Are dependencies pinned to specific versions? Are there any deprecated or potentially vulnerable packages imported?",
    "weight": 10
  },
  {
    "id": "error_handling",
    "category": "Error Handling & Information Disclosure",
    "question": "Are there broad exception handlers that swallow errors silently, or error messages that expose stack traces or internal details?",
    "weight": 10
  },
  {
    "id": "crypto",
    "category": "Cryptography",
    "question": "Are there any weak hashing algorithms (MD5, SHA1), weak encryption, or insecure random number generation?",
    "weight": 15
  },
  {
    "id": "input_validation",
    "category": "Input Validation",
    "question": "Is user input validated and sanitized before being processed? Are there missing length checks or type validations?",
    "weight": 10
  }
]

SEVERITY_PROMPT_SUFFIX = """
IMPORTANT: Keep your detailed analysis strictly between 150-200 words. Provide specific details but be concise.

After your analysis, on the very last line write exactly:
SEVERITY: <CRITICAL|HIGH|MEDIUM|LOW|NONE>
Where:
- CRITICAL: active exploitable vulnerability found with evidence in code
- HIGH: likely vulnerability with clear code evidence
- MEDIUM: potential issue, needs review
- LOW: minor concern or best practice violation
- NONE: no issues found in retrieved code
"""

async def run_risk_analysis(repo_id: str) -> dict:
  findings = []
  total_weight = sum(q["weight"] for q in SECURITY_QUESTIONS)
  risk_deductions = 0

  for sq in SECURITY_QUESTIONS:
    question_with_suffix = sq["question"] + SEVERITY_PROMPT_SUFFIX
    try:
      result = await run_query(repo_id, question_with_suffix, user_id=None, save_to_db=False)
      answer = result.get("answer", "")
      citations = result.get("citations", [])

      severity = "NONE"
      for line in reversed(answer.strip().split("\n")):
        if line.startswith("SEVERITY:"):
          severity = line.replace("SEVERITY:", "").strip()
          answer = answer[:answer.rfind("SEVERITY:")].strip()
          break

      deduction_map = {
        "CRITICAL": 1.0, "HIGH": 0.7,
        "MEDIUM": 0.4, "LOW": 0.1, "NONE": 0.0
      }
      deduction = sq["weight"] * deduction_map.get(severity, 0.0)
      risk_deductions += deduction

      findings.append({
        "id": sq["id"],
        "category": sq["category"],
        "severity": severity,
        "answer": answer,
        "citations": citations,
        "weight": sq["weight"]
      })
    except Exception as e:
      findings.append({
        "id": sq["id"],
        "category": sq["category"],
        "severity": "NONE",
        "answer": f"Analysis failed: {str(e)}",
        "citations": [],
        "weight": sq["weight"]
      })

  score = max(0, round(100 - (risk_deductions / total_weight) * 100))

  if score >= 80:
    grade = "A"
  elif score >= 65:
    grade = "B"
  elif score >= 50:
    grade = "C"
  elif score >= 35:
    grade = "D"
  else:
    grade = "F"

  return {
    "repo_id": repo_id,
    "score": score,
    "grade": grade,
    "findings": findings,
    "critical_count": sum(1 for f in findings if f["severity"] == "CRITICAL"),
    "high_count": sum(1 for f in findings if f["severity"] == "HIGH"),
    "medium_count": sum(1 for f in findings if f["severity"] == "MEDIUM"),
    "low_count": sum(1 for f in findings if f["severity"] == "LOW"),
    "analyzed_at": datetime.utcnow().isoformat() + "Z"
  }

async def start_risk_analysis(repo_id: str):
  db = get_database()
  if db is None:
    return
  
  await db["risk_reports"].update_one(
    {"repo_id": repo_id},
    {"$set": {"status": "running", "error": None}},
    upsert=True
  )

  try:
    report = await run_risk_analysis(repo_id)
    report["status"] = "complete"
    await db["risk_reports"].update_one(
      {"repo_id": repo_id},
      {"$set": report},
      upsert=True
    )
  except Exception as e:
    await db["risk_reports"].update_one(
      {"repo_id": repo_id},
      {"$set": {"status": "failed", "error": str(e)}},
      upsert=True
    )
