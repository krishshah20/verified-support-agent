"""
Day 1: Verify data is ready
Run: python scripts/day1_verify.py
"""

import json
from pathlib import Path

print("=" * 60)
print("DAY 1: DATA VERIFICATION")
print("=" * 60)

checks = []

# Check 1: Raw data exists
print("\n[CHECK 1] Raw data files...")
raw_docs = Path("data/raw/fastapi_docs/docs.json")
raw_issues = Path("data/raw/github_issues/issues.json")

if raw_docs.exists():
    with open(raw_docs) as f:
        docs = json.load(f)
    print(f"  ✓ FastAPI docs: {len(docs)} documents")
    checks.append(True)
else:
    print(f"  ✗ Missing: data/raw/fastapi_docs/docs.json")
    checks.append(False)

if raw_issues.exists():
    with open(raw_issues) as f:
        issues = json.load(f)
    print(f"  ✓ GitHub issues: {len(issues)} issues")
    checks.append(True)
else:
    print(f"  ✗ Missing: data/raw/github_issues/issues.json")
    checks.append(False)

# Check 2: Processed chunks exist
print("\n[CHECK 2] Processed chunks...")
processed = Path("data/processed/all_chunks.json")

if processed.exists():
    with open(processed) as f:
        chunks = json.load(f)
    print(f"  ✓ All chunks: {len(chunks)} total")
    
    # Breakdown by source
    sources = {}
    for chunk in chunks:
        src = chunk['source']
        sources[src] = sources.get(src, 0) + 1
    
    for src, count in sources.items():
        print(f"    - {src}: {count} chunks")
    checks.append(True)
else:
    print(f"  ✗ Missing: data/processed/all_chunks.json")
    checks.append(False)

# Check 3: Data quality
print("\n[CHECK 3] Data quality...")

if processed.exists():
    with open(processed) as f:
        chunks = json.load(f)
    
    if chunks:
        min_length = min(len(c['content']) for c in chunks)
        max_length = max(len(c['content']) for c in chunks)
        avg_length = sum(len(c['content']) for c in chunks) / len(chunks)
        
        print(f"  ✓ Chunk length stats:")
        print(f"    - Min: {min_length} chars")
        print(f"    - Max: {max_length} chars")
        print(f"    - Avg: {avg_length:.0f} chars")
        
        if len(chunks) >= 30:
            print(f"  ✓ Sufficient chunk count ({len(chunks)} chunks)")
            checks.append(True)
        else:
            print(f"  ⚠ Low chunk count: {len(chunks)} (expect 50+)")
            checks.append(False)
    else:
        print(f"  ✗ No chunks found")
        checks.append(False)

# Summary
print("\n" + "=" * 60)
print("VERIFICATION SUMMARY")
print("=" * 60)

if all(checks):
    print("\n✓✓✓ ALL CHECKS PASSED ✓✓✓")
    print("\n✓ DAY 1 COMPLETE!")
    print("\nYou now have:")
    print("  - FastAPI documentation chunks")
    print("  - GitHub issues chunks")
    print("  - Ready for Week 1 retrieval pipeline")
else:
    print("\n✗ SOME CHECKS FAILED")
    print("\nTroubleshooting:")
    print("  1. Make sure you ran day1_gather_data.py first")
    print("  2. Make sure you ran day1_process_data.py second")
    print("  3. Check that data/ directory has correct structure")