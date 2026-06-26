"""
Day 1: Gather FastAPI docs + GitHub issues
Run: python scripts/day1_gather_data.py
"""

import json
import os
from pathlib import Path
import requests
from datetime import datetime

# Create data directories
Path("data/raw/fastapi_docs").mkdir(parents=True, exist_ok=True)
Path("data/raw/github_issues").mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("DAY 1: FASTAPI DATA GATHERING")
print("=" * 60)

# ============= PART 1: FastAPI Official Docs =============
print("\n[1/2] Fetching FastAPI official documentation...")

fastapi_docs_urls = [
    "https://raw.githubusercontent.com/tiangolo/fastapi/master/docs/en/docs/index.md",
    "https://raw.githubusercontent.com/tiangolo/fastapi/master/docs/en/docs/tutorial/first-steps.md",
    "https://raw.githubusercontent.com/tiangolo/fastapi/master/docs/en/docs/tutorial/path-parameters.md",
    "https://raw.githubusercontent.com/tiangolo/fastapi/master/docs/en/docs/tutorial/query-parameters.md",
    "https://raw.githubusercontent.com/tiangolo/fastapi/master/docs/en/docs/tutorial/request-body.md",
    "https://raw.githubusercontent.com/tiangolo/fastapi/master/docs/en/docs/tutorial/response-model.md",
    "https://raw.githubusercontent.com/tiangolo/fastapi/master/docs/en/docs/tutorial/status-codes.md",
    "https://raw.githubusercontent.com/tiangolo/fastapi/master/docs/en/docs/advanced/middleware.md",
    "https://raw.githubusercontent.com/tiangolo/fastapi/master/docs/en/docs/advanced/dependency-injection.md",
    "https://raw.githubusercontent.com/tiangolo/fastapi/master/docs/en/docs/advanced/security/intro.md",
]

docs_data = []
for i, url in enumerate(fastapi_docs_urls, 1):
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            filename = url.split('/')[-1].replace('.md', '')
            docs_data.append({
                "id": f"fastapi_docs_{i}",
                "source": "fastapi_docs",
                "title": filename,
                "url": url,
                "content": resp.text,
                "timestamp": datetime.now().isoformat()
            })
            print(f"  ✓ Downloaded: {filename}")
        else:
            print(f"  ✗ Failed (status {resp.status_code}): {url}")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")

with open("data/raw/fastapi_docs/docs.json", "w") as f:
    json.dump(docs_data, f, indent=2)
print(f"\n✓ Saved {len(docs_data)} FastAPI docs")

# ============= PART 2: GitHub Issues =============
print("\n[2/2] Fetching FastAPI GitHub issues...")

github_url = "https://api.github.com/repos/tiangolo/fastapi/issues"
params = {
    "state": "all",
    "per_page": 50,
    "sort": "updated",
    "direction": "desc"
}

issues_data = []
try:
    resp = requests.get(github_url, params=params, timeout=10)
    
    if resp.status_code == 200:
        issues = resp.json()
        
        for issue in issues:
            # Only get issues with some discussion (comments > 1)
            if issue.get("comments", 0) > 1:
                issues_data.append({
                    "id": f"github_issue_{issue['number']}",
                    "source": "github_issues",
                    "title": issue["title"],
                    "url": issue["html_url"],
                    "body": issue["body"] or "",
                    "comments_count": issue["comments"],
                    "created_at": issue["created_at"],
                    "updated_at": issue["updated_at"],
                    "timestamp": datetime.now().isoformat()
                })
        
        print(f"  ✓ Fetched {len(issues)} issues (keeping {len(issues_data)} with discussion)")
    else:
        print(f"  ✗ GitHub API error: {resp.status_code}")

except Exception as e:
    print(f"  ✗ Error: {str(e)}")

with open("data/raw/github_issues/issues.json", "w") as f:
    json.dump(issues_data, f, indent=2)
print(f"\n✓ Saved {len(issues_data)} GitHub issues")

# ============= SUMMARY =============
print("\n" + "=" * 60)
print("✓ DAY 1 PART 1 COMPLETE")
print("=" * 60)
print(f"\n✓ FastAPI docs: {len(docs_data)} documents")
print(f"✓ GitHub issues: {len(issues_data)} issues")
print(f"✓ Total raw documents: {len(docs_data) + len(issues_data)}")
print(f"\nNext: Run 'python scripts/day1_process_data.py'")