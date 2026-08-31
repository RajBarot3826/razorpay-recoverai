# -*- coding: utf-8 -*-
"""Quick test script for RecoverAI pipeline."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import httpx
import json

print("=" * 60)
print("  RecoverAI - 100 Transaction Pipeline Test")
print("=" * 60)

r = httpx.post("http://localhost:8000/api/demo", json={"count": 100}, timeout=60)
d = r.json()
s = d["results_summary"]
m = d["metrics"]
ba = d["before_after"]

print(f"\nRESULTS SUMMARY")
print(f"  Total Transactions: {s['total']}")
print(f"  Recovered:          {s['recovered']} ({s['recovery_rate']})")
print(f"  Failed:             {s['failed']}")
print(f"  Revenue Recovered:  Rs {m['total_revenue_recovered']:,.2f}")

print(f"\nBY FAILURE TYPE")
for k, v in m["by_failure_type"].items():
    rate = (v["recovered"] / v["processed"] * 100) if v["processed"] > 0 else 0
    print(f"  {k:25s}: {v['recovered']:3d}/{v['processed']:3d} ({rate:.0f}%)")

print(f"\nBY ACTION TYPE")
for k, v in m["by_action_type"].items():
    rate = (v["recovered"] / v["processed"] * 100) if v["processed"] > 0 else 0
    print(f"  {k:25s}: {v['recovered']:3d}/{v['processed']:3d} ({rate:.0f}%)")

print(f"\nAI vs BASELINE COMPARISON")
print(f"  Baseline Recovery Rate: {ba['baseline']['recovery_rate']*100:.1f}%  ({ba['baseline']['recovered_count']} txns, Rs {ba['baseline']['revenue_recovered']:,.2f})")
print(f"  AI Recovery Rate:       {ba['ai']['recovery_rate']*100:.1f}%  ({ba['ai']['recovered_count']} txns, Rs {ba['ai']['revenue_recovered']:,.2f})")
print(f"  Recovery Lift:          +{ba['lift']['absolute_rate_increase']*100:.1f}%  (+{ba['lift']['additional_recovered_count']} txns, +Rs {ba['lift']['additional_revenue']:,.2f})")

# Show a sample audit trail
print(f"\nSAMPLE AUDIT TRAIL (first transaction)")
if d.get("sample_results") and len(d["sample_results"]) > 0:
    sample = d["sample_results"][0]
    print(f"  Transaction: {sample['transaction_id']}")
    print(f"  Amount:      Rs {sample['original_amount']:,.2f}")
    print(f"  Failure:     {sample['failure_type']}")
    print(f"  Root Cause:  {sample['root_cause']}")
    print(f"  Recovered:   {'YES' if sample['success'] else 'NO'}")
    print(f"  Actions:")
    for a in sample.get("actions_taken", []):
        print(f"    -> [{a['status']:10s}] {a['action_type']} -- {a.get('outcome', 'N/A')}")
    print(f"  Audit Trail:")
    for e in sample.get("audit_trail", []):
        print(f"    [{e['agent_name']:20s}] {e['action']:20s} -> {e['outcome']}")

print(f"\n{'=' * 60}")
print(f"  Pipeline test complete!")
print(f"{'=' * 60}")
