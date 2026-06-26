"""
Day 1: Process raw data into chunks
Run: python scripts/day1_process_data.py
"""

import json
from pathlib import Path

print("=" * 60)
print("DAY 1: PROCESSING RAW DATA INTO CHUNKS")
print("=" * 60)

Path("data/processed").mkdir(parents=True, exist_ok=True)

all_chunks = []
chunk_counter = 0

# ============= Process FastAPI Docs =============
print("\n[1/2] Processing FastAPI documentation...")

try:
    with open("data/raw/fastapi_docs/docs.json") as f:
        docs = json.load(f)
    
    for doc in docs:
        content = doc["content"]
        
        # Split by double newlines (paragraphs)
        paragraphs = content.split("\n\n")
        
        for para_idx, para in enumerate(paragraphs):
            if len(para.strip()) < 30:  # Skip tiny chunks
                continue
            
            chunk_counter += 1
            chunk = {
                "id": f"chunk_{chunk_counter}",
                "document_id": doc["id"],
                "content": para.strip(),
                "chunk_type": "fixed",
                "source": "fastapi_docs",
                "metadata": {
                    "title": doc["title"],
                    "url": doc["url"],
                    "doc_source": "fastapi_official",
                    "para_index": para_idx
                }
            }
            all_chunks.append(chunk)
    
    docs_chunks = chunk_counter
    print(f"  ✓ Created {docs_chunks} chunks from {len(docs)} docs")

except Exception as e:
    print(f"  ✗ Error processing docs: {str(e)}")
    docs_chunks = 0

# ============= Process GitHub Issues =============
print("\n[2/2] Processing GitHub issues...")

try:
    with open("data/raw/github_issues/issues.json") as f:
        issues = json.load(f)
    
    issues_before = chunk_counter
    
    for issue in issues:
        # Combine title + body as one chunk per issue
        content = f"**{issue['title']}**\n\n{issue['body']}"
        
        if len(content.strip()) < 50:
            continue
        
        chunk_counter += 1
        chunk = {
            "id": f"chunk_{chunk_counter}",
            "document_id": issue["id"],
            "content": content.strip(),
            "chunk_type": "fixed",
            "source": "github_issues",
            "metadata": {
                "title": issue["title"],
                "url": issue["url"],
                "comments": issue["comments_count"],
                "updated": issue["updated_at"],
                "doc_source": "fastapi_github"
            }
        }
        all_chunks.append(chunk)
    
    issues_chunks = chunk_counter - issues_before
    print(f"  ✓ Created {issues_chunks} chunks from {len(issues)} issues")

except Exception as e:
    print(f"  ✗ Error processing issues: {str(e)}")

# ============= Save Processed Chunks =============
print("\n" + "=" * 60)
print("✓ PROCESSING COMPLETE")
print("=" * 60)

with open("data/processed/all_chunks.json", "w") as f:
    json.dump(all_chunks, f, indent=2)

print(f"\n✓ Total chunks created: {chunk_counter}")
print(f"✓ Saved to: data/processed/all_chunks.json")

if all_chunks:
    print(f"\n✓ Chunk sample (first chunk):")
    print(f"  ID: {all_chunks[0]['id']}")
    print(f"  Source: {all_chunks[0]['source']}")
    print(f"  Content preview: {all_chunks[0]['content'][:80]}...")

print(f"\nNext: Run 'python scripts/day1_verify.py'")