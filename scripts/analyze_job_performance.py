#!/usr/bin/env python3
"""
Performance analysis script to understand why a job took so long.
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mobius.storage.jobs import JobStorage


async def analyze_job_performance(job_id: str):
    """Analyze a job's performance and identify bottlenecks."""
    
    print(f"⏱️  Performance Analysis for Job: {job_id}")
    print("=" * 60)
    
    try:
        job_storage = JobStorage()
        job = await job_storage.get_job(job_id)
        
        if not job:
            print(f"❌ Job not found: {job_id}")
            return False
        
        print(f"📊 Job Overview:")
        print(f"   Status: {job.status}")
        print(f"   Brand ID: {job.brand_id}")
        print(f"   Progress: {job.progress}%")
        
        # Parse timestamps
        created_at = job.created_at
        updated_at = job.updated_at
        
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        
        total_duration = (updated_at - created_at).total_seconds()
        
        print(f"   Created: {created_at}")
        print(f"   Updated: {updated_at}")
        print(f"   Total Duration: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
        
        # Analyze job state
        state = job.state or {}
        attempt_count = state.get("attempt_count", 0)
        audit_history = state.get("audit_history", [])
        compliance_scores = state.get("compliance_scores", [])
        
        print(f"\n🔄 Generation Attempts:")
        print(f"   Attempt Count: {attempt_count}")
        print(f"   Audit History Length: {len(audit_history)}")
        print(f"   Compliance Scores: {len(compliance_scores)}")
        
        # Estimate time breakdown
        if attempt_count > 0:
            avg_time_per_attempt = total_duration / attempt_count
            print(f"   Average Time per Attempt: {avg_time_per_attempt:.1f} seconds")
            
            if avg_time_per_attempt > 60:
                print(f"   ⚠️  WARNING: Each attempt is taking over 1 minute!")
        
        # Analyze compliance scores
        if compliance_scores:
            print(f"\n📈 Compliance Score History:")
            for i, score in enumerate(compliance_scores, 1):
                overall = score.get("overall_score", 0)
                print(f"   Attempt {i}: {overall}% compliance")
        
        # Check for specific performance issues
        print(f"\n🔍 Performance Issues Analysis:")
        
        issues_found = []
        
        # Issue 1: Too many attempts
        if attempt_count > 3:
            issues_found.append(f"High attempt count ({attempt_count}) - suggests generation quality issues")
        
        # Issue 2: Long total duration
        if total_duration > 300:  # 5 minutes
            issues_found.append(f"Long total duration ({total_duration/60:.1f} min) - suggests API timeouts or retries")
        
        # Issue 3: Missing logo flag (from our diagnosis)
        if "original_had_logos" not in state:
            issues_found.append("Missing 'original_had_logos' flag - may cause logo fetching issues")
        
        # Issue 4: User decision indicates problems
        user_decision = state.get("user_decision")
        if user_decision == "tweak":
            issues_found.append("User requested tweak - indicates initial generation wasn't satisfactory")
        
        # Issue 5: Low compliance scores
        if compliance_scores:
            low_scores = [s for s in compliance_scores if s.get("overall_score", 0) < 80]
            if low_scores:
                issues_found.append(f"Low compliance scores in {len(low_scores)} attempts - suggests brand guideline issues")
        
        if issues_found:
            print(f"   Found {len(issues_found)} potential issues:")
            for i, issue in enumerate(issues_found, 1):
                print(f"   {i}. {issue}")
        else:
            print(f"   ✅ No obvious performance issues detected")
        
        # Recommendations
        print(f"\n💡 Performance Recommendations:")
        
        recommendations = []
        
        if attempt_count > 2:
            recommendations.append("Consider improving prompt optimization to reduce retry attempts")
        
        if total_duration > 180:  # 3 minutes
            recommendations.append("Investigate API timeout settings and retry logic")
        
        if "original_had_logos" not in state:
            recommendations.append("Apply the logo preservation fix to prevent logo-related issues")
        
        if compliance_scores and any(s.get("overall_score", 0) < 70 for s in compliance_scores):
            recommendations.append("Review brand guidelines quality and compressed twin generation")
        
        if len(audit_history) != attempt_count:
            recommendations.append("Check audit node performance - audit history length mismatch")
        
        if not recommendations:
            recommendations.append("Performance appears normal for this job complexity")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        # Estimate expected vs actual performance
        print(f"\n⏱️  Performance Expectations:")
        
        expected_time_per_attempt = 30  # seconds
        expected_total = expected_time_per_attempt * attempt_count
        
        print(f"   Expected time per attempt: ~{expected_time_per_attempt}s")
        print(f"   Expected total for {attempt_count} attempts: ~{expected_total}s ({expected_total/60:.1f} min)")
        print(f"   Actual total: {total_duration:.1f}s ({total_duration/60:.1f} min)")
        
        if total_duration > expected_total * 1.5:
            performance_ratio = total_duration / expected_total
            print(f"   ⚠️  SLOW: Job took {performance_ratio:.1f}x longer than expected")
        else:
            print(f"   ✅ NORMAL: Job performance within expected range")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing job performance: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/analyze_job_performance.py <job_id>")
        print("")
        print("This script analyzes why a job took a long time to complete.")
        sys.exit(1)
    
    job_id = sys.argv[1]
    result = asyncio.run(analyze_job_performance(job_id))
    
    sys.exit(0 if result else 1)