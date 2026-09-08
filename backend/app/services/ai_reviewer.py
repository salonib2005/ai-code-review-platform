import httpx
import json

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
MODEL = "qwen2.5-coder:7b"


def find_line_number(source_code, code_snippet):
    """Find the actual line number of the problematic code."""

    if not code_snippet:
        return None

    source_lines = source_code.splitlines()

    snippet_lines = [
        line.rstrip()
        for line in code_snippet.strip().splitlines()
    ]

    while snippet_lines and not snippet_lines[0].strip():
        snippet_lines.pop(0)

    while snippet_lines and not snippet_lines[-1].strip():
        snippet_lines.pop()

    if not snippet_lines:
        return None

    # Exact multi-line match
    for i in range(
        len(source_lines) - len(snippet_lines) + 1
    ):
        source_section = [
            line.rstrip()
            for line in source_lines[
                i:i + len(snippet_lines)
            ]
        ]

        if source_section == snippet_lines:
            return i + 1

    # Whitespace-normalized match
    normalized_snippet = [
        " ".join(line.split())
        for line in snippet_lines
    ]

    for i in range(
        len(source_lines) - len(snippet_lines) + 1
    ):
        source_section = [
            " ".join(line.split())
            for line in source_lines[
                i:i + len(snippet_lines)
            ]
        ]

        if source_section == normalized_snippet:
            return i + 1

    # Match first meaningful line
    first_line = " ".join(
        snippet_lines[0].split()
    )

    if first_line:
        for i, source_line in enumerate(source_lines):
            if " ".join(source_line.split()) == first_line:
                return i + 1

    return None


def review_single_file(file_path, file_content):
    """Review one source file using the local Qwen model."""

    prompt = f"""
You are a senior software engineer performing a STRICT code review.

Analyze ONLY the source code provided below.

FILE:
{file_path}

SOURCE CODE:
{file_content}

Identify ONLY genuine, actionable issues.

Look for:

* Actual bugs
* Runtime errors
* Security vulnerabilities
* Authentication or authorization flaws
* Missing error handling that causes incorrect behavior
* Input validation vulnerabilities
* SQL injection
* Command injection
* Path traversal
* XSS
* Hardcoded credentials
* Incorrect API usage
* Serious reliability problems

STRICT RULES:

1. Only report issues directly supported by the source code.

2. Do NOT give generic security advice.

3. Environment variables are correct for storing secrets.
   Do NOT report os.getenv() usage as a vulnerability.

4. Do NOT report temporary variables containing access tokens
   merely because they exist in memory.

5. Do NOT report hypothetical attacks without evidence.

6. Do NOT duplicate issues.

7. Do NOT report standard FastAPI + SQLAlchemy dependency
   patterns as thread-safety problems.

8. A SQLAlchemy Session created per request using a dependency
   with yield is a valid pattern.

9. Only report database session problems if the SAME session
   is clearly shared across requests, threads, or concurrent tasks.

10. Do NOT report datetime.utcnow(), datetime.now(),
    UTC timestamps, or datetime defaults as problems by themselves.

11. Do NOT report timezone choices unless the source code
    clearly demonstrates incorrect behavior.

12. Do NOT report normal framework defaults as defects.

13. Do NOT report something merely because another implementation
    might be preferable.

14. Do NOT report unused imports unless they directly cause
    a runtime error.

15. Do NOT report unused variables or type annotations as issues.

16. Do NOT report placeholder UI text as an issue.

17. Do NOT report empty or minimal configuration files as issues.

18. Do NOT report missing optional framework configuration.

19. Do NOT report performance improvements unless the current
    implementation causes a serious demonstrated performance problem.

20. Do NOT report normal database connection/session management.

21. Do NOT report missing error handling unless an actual failure
    path is clearly present and would cause incorrect behavior.

22. A code-review issue must describe something actually wrong
    with the current implementation.

23. When uncertain whether something is a genuine defect,
    DO NOT report it.

24. Prefer fewer accurate issues over many speculative issues.

25. If there are no genuine issues, return an empty issues list.

IMPORTANT CODE SNIPPET RULE:

For every reported issue, return the EXACT source-code line
that demonstrates the problem.

The code_snippet MUST be copied character-for-character
from the provided source code.

DO NOT rewrite the code.

DO NOT add indentation.

DO NOT remove indentation.

DO NOT add comments.

DO NOT combine unrelated lines.

Prefer exactly ONE source-code line per issue.

If you cannot provide an exact source-code line proving the
issue, DO NOT report the issue.

Severity:

* warning = genuine bug, security issue, runtime/reliability problem
* suggestion = meaningful non-critical improvement

Return ONLY valid JSON.

Use exactly this structure:

{{
    "issues": [
        {{
            "file": "{file_path}",
            "code_snippet": "EXACT SOURCE LINE",
            "severity": "warning",
            "message": "Clear explanation of the genuine problem."
        }}
    ]
}}

Severity must be exactly:

* warning
* suggestion

If there are no genuine issues:

{{
    "issues": []
}}
"""

    response = httpx.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=300.0,
    )

    response.raise_for_status()

    data = response.json()

    result = data["response"].strip()

    # Remove markdown code fences if Qwen adds them
    if result.startswith("```json"):
        result = result[7:]
    elif result.startswith("```"):
        result = result[3:]

    if result.endswith("```"):
        result = result[:-3]

    result = result.strip()

    return json.loads(result)


def review_code(files):
    """
    Review repository files individually and combine
    all AI-generated issues into one result.
    """

    all_issues = []

    total_files = len(files)

    for index, file in enumerate(files, start=1):

        file_path = file["path"]
        file_content = file["content"]

        print(
            f"[{index}/{total_files}] Reviewing: {file_path}"
        )

        try:

            result = review_single_file(
                file_path,
                file_content
            )

            issues = result.get("issues", [])

            verified_issues = []

            for issue in issues:

                code_snippet = issue.get(
                    "code_snippet",
                    ""
                )

                actual_line = find_line_number(
                    file_content,
                    code_snippet
                )

                # Reject hallucinated snippets
                if actual_line is None:

                    print(
                        "    Skipping issue: "
                        "could not locate code snippet"
                    )

                    continue

                severity = issue.get(
                    "severity",
                    "warning"
                )

                if severity not in (
                    "warning",
                    "suggestion"
                ):
                    severity = "warning"

                verified_issue = {
                    "file": file_path,
                    "line": actual_line,
                    "severity": severity,
                    "message": issue.get(
                        "message",
                        "Genuine issue detected."
                    )
                }

                verified_issues.append(
                    verified_issue
                )

            all_issues.extend(
                verified_issues
            )

            print(
                f"    Issues found: "
                f"{len(verified_issues)}"
            )

        except Exception as error:

            print(
                f"    Error reviewing "
                f"{file_path}: {error}"
            )

    return {
        "issues": all_issues
    }