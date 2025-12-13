#!/usr/bin/env python3
"""
Helper script to find recent jobs, especially failed or problematic ones.
This makes it easier to identify which job to diagnose.
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mobius.storage.jobs import JobStorage


async def find_recent_jobs(limit: int = 10, status_filter: str = None):
    """Find recent jobs, optionally filtered by status."""
    
    print(f"🔍 Finding Recent Jobs")
    if status_filter:
        print(f"   Filter: status = {status_filter}")
    print(f"   Limit: {limit}")
    print("=" * 50)
    
    try:
        job_storage = JobStorage()
        
        # Get recent jobs using the correct JobStorage API
        jobs = await job_storage.list_jobs(limit=limit)
        
        if not jobs:
            print("❌ No jobs found")
            return []
        
        # Filter by status if specified
        if status_filter:
            jobs = [job for job in jobs if job.status == status_filter]
            if not jobs:
                print(f"❌ No jobs found with status: {status_filter}")
                return []
        
        # Sort by created_at (most recent first)
        jobs.sort(key=lambda x: x.created_at, reverse=True)
        
        print(f"Found {len(jobs)} jobs:")
        print()
        
        for i, job in enumerate(jobs, 1):
            # Format the timestamp
            if isinstance(job.created_at, str):
                created_str = job.created_at
            else:
                created_str = job.created_at.strftime("%Y-%m-%d %H:%M:%S")
            
            # Get state info
            state = job.state or {}
            attempt_count = state.get("attempt_count", 0)
            has_original_had_logos = "original_had_logos" in state
            original_had_logos = state.get("original_had_logos")
            
            # Status indicator
            status_emoji = {
                "completed": "✅",
                "failed": "❌", 
                "needs_review": "⏸️",
                "processing": "⏳",
                "correcting": "🔄",
                "pending": "⏳"
            }.get(job.status, "❓")
            
            print(f"{i:2d}. {status_emoji} {job.job_id}")
            print(f"     Status: {job.status}")
            print(f"     Brand: {job.brand_id}")
            print(f"     Created: {created_str}")
            print(f"     Progress: {job.progress}%")
            print(f"     Attempts: {attempt_count}")
            print(f"     Has logo flag: {has_original_had_logos} ({original_had_logos})")
            print()
        
        return jobs
        
    except Exception as e:
        print(f"❌ Error finding jobs: {e}")
        return []


async def find_latest_job():
    """Find the single most recent job."""
    
    jobs = await find_recent_jobs(limit=1)
    if jobs:
        latest = jobs[0]
        print(f"🎯 Latest Job: {latest.job_id}")
        print(f"   Status: {latest.status}")
        print(f"   Created: {latest.created_at}")
        return latest.job_id
    return None


async def find_problematic_jobs():
    """Find jobs that might have logo issues."""
    
    print(f"🚨 Finding Potentially Problematic Jobs")
    print("=" * 50)
    
    # Look for failed jobs, needs_review jobs, or jobs with multiple attempts
    jobs = await find_recent_jobs(limit=20)
    
    problematic = []
    
    for job in jobs:
        state = job.state or {}
        attempt_count = state.get("attempt_count", 0)
        is_tweak = state.get("is_tweak", False)
        has_logo_flag = "original_had_logos" in state
        
        # Criteria for problematic jobs
        is_problematic = (
            job.status in ["failed", "needs_review"] or
            attempt_count > 1 or
            is_tweak or
            not has_logo_flag
        )
        
        if is_problematic:
            problematic.append(job)
    
    if not problematic:
        print("✅ No obviously problematic jobs found")
        return []
    
    print(f"Found {len(problematic)} potentially problematic jobs:")
    print()
    
    for i, job in enumerate(problematic, 1):
        state = job.state or {}
        attempt_count = state.get("attempt_count", 0)
        is_tweak = state.get("is_tweak", False)
        has_logo_flag = "original_had_logos" in state
        original_had_logos = state.get("original_had_logos")
        
        issues = []
        if job.status in ["failed", "needs_review"]:
            issues.append(f"status={job.status}")
        if attempt_count > 1:
            issues.append(f"attempts={attempt_count}")
        if is_tweak:
            issues.append("is_tweak=True")
        if not has_logo_flag:
            issues.append("missing_logo_flag")
        
        print(f"{i:2d}. 🚨 {job.job_id}")
        print(f"     Issues: {', '.join(issues)}")
        print(f"     Brand: {job.brand_id}")
        print(f"     Logo flag: {original_had_logos}")
        print()
    
    return problematic


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "latest":
            job_id = asyncio.run(find_latest_job())
            if job_id:
                print(f"\nTo diagnose this job, run:")
                print(f"python scripts/diagnose_real_job.py {job_id}")
        
        elif command == "failed":
            asyncio.run(find_recent_jobs(limit=10, status_filter="failed"))
        
        elif command == "review":
            asyncio.run(find_recent_jobs(limit=10, status_filter="needs_review"))
        
        elif command == "problems":
            jobs = asyncio.run(find_problematic_jobs())
            if jobs:
                print(f"\nTo diagnose any of these jobs, run:")
                print(f"python scripts/diagnose_real_job.py <job_id>")
        
        else:
            print(f"Unknown command: {command}")
            print("Available commands: latest, failed, review, problems")
    
    else:
        print("Usage:")
        print("  python scripts/find_recent_jobs.py latest     # Find the most recent job")
        print("  python scripts/find_recent_jobs.py failed     # Find recent failed jobs")
        print("  python scripts/find_recent_jobs.py review     # Find jobs needing review")
        print("  python scripts/find_recent_jobs.py problems   # Find potentially problematic jobs")
        print("")
        print("Or run without arguments to see recent jobs:")
        asyncio.run(find_recent_jobs())