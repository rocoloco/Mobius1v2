#!/usr/bin/env python3
"""
Script to check for stuck jobs in the database and optionally mark them as failed.

This helps diagnose and fix issues where jobs get stuck in 'pending' or 'processing' 
state due to backend crashes or timeouts.
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from mobius.storage.jobs import JobStorage
from mobius.models.job import Job


async def find_stuck_jobs(older_than_minutes: int = 5) -> List[Job]:
    """Find jobs that are stuck in non-terminal states for too long."""
    job_storage = JobStorage()
    
    # Get all jobs in non-terminal states
    non_terminal_statuses = ['pending', 'processing', 'generating', 'auditing', 'correcting']
    stuck_jobs = []
    
    for status in non_terminal_statuses:
        jobs = await job_storage.list_jobs(status=status)
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=older_than_minutes)
        
        for job in jobs:
            # Parse created_at if it's a string
            if isinstance(job.created_at, str):
                created_at = datetime.fromisoformat(job.created_at.replace('Z', '+00:00'))
            else:
                created_at = job.created_at
                
            if created_at < cutoff_time:
                stuck_jobs.append(job)
    
    return stuck_jobs


async def mark_jobs_as_failed(job_ids: List[str], reason: str = "Marked as failed due to timeout") -> None:
    """Mark specified jobs as failed."""
    job_storage = JobStorage()
    
    for job_id in job_ids:
        try:
            await job_storage.update_job(job_id, {
                "status": "failed",
                "state": {
                    "error": reason,
                    "marked_failed_at": datetime.now(timezone.utc).isoformat()
                }
            })
            print(f"✓ Marked job {job_id} as failed")
        except Exception as e:
            print(f"✗ Failed to update job {job_id}: {e}")


async def main():
    """Main function to check and optionally fix stuck jobs."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check for stuck jobs")
    parser.add_argument(
        "--older-than", 
        type=int, 
        default=5, 
        help="Find jobs older than N minutes (default: 5)"
    )
    parser.add_argument(
        "--fix", 
        action="store_true", 
        help="Mark stuck jobs as failed"
    )
    parser.add_argument(
        "--job-id",
        type=str,
        help="Check specific job ID"
    )
    
    args = parser.parse_args()
    
    try:
        if args.job_id:
            # Check specific job
            job_storage = JobStorage()
            job = await job_storage.get_job(args.job_id)
            
            if not job:
                print(f"Job {args.job_id} not found")
                return
            
            print(f"Job {args.job_id}:")
            print(f"  Status: {job.status}")
            print(f"  Created: {job.created_at}")
            print(f"  Updated: {job.updated_at}")
            print(f"  Brand ID: {job.brand_id}")
            
            if job.state:
                print(f"  State: {job.state}")
            
            # Check if it's stuck
            if isinstance(job.created_at, str):
                created_at = datetime.fromisoformat(job.created_at.replace('Z', '+00:00'))
            else:
                created_at = job.created_at
                
            age_minutes = (datetime.now(timezone.utc) - created_at).total_seconds() / 60
            
            if job.status in ['pending', 'processing', 'generating'] and age_minutes > args.older_than:
                print(f"  ⚠️  Job appears stuck (running for {age_minutes:.1f} minutes)")
                
                if args.fix:
                    await mark_jobs_as_failed([args.job_id], f"Job stuck in {job.status} state for {age_minutes:.1f} minutes")
            else:
                print(f"  ✓ Job appears normal")
        
        else:
            # Check all stuck jobs
            print(f"Checking for jobs stuck longer than {args.older_than} minutes...")
            
            stuck_jobs = await find_stuck_jobs(args.older_than)
            
            if not stuck_jobs:
                print("✓ No stuck jobs found")
                return
            
            print(f"\nFound {len(stuck_jobs)} stuck jobs:")
            print("-" * 80)
            
            for job in stuck_jobs:
                # Calculate age
                if isinstance(job.created_at, str):
                    created_at = datetime.fromisoformat(job.created_at.replace('Z', '+00:00'))
                else:
                    created_at = job.created_at
                    
                age_minutes = (datetime.now(timezone.utc) - created_at).total_seconds() / 60
                
                print(f"Job {job.job_id}:")
                print(f"  Status: {job.status}")
                print(f"  Age: {age_minutes:.1f} minutes")
                print(f"  Brand: {job.brand_id}")
                
                if job.state and 'prompt' in job.state:
                    prompt = job.state['prompt'][:50] + "..." if len(job.state['prompt']) > 50 else job.state['prompt']
                    print(f"  Prompt: {prompt}")
                
                print()
            
            if args.fix:
                print("Marking stuck jobs as failed...")
                job_ids = [job.job_id for job in stuck_jobs]
                await mark_jobs_as_failed(job_ids, f"Job stuck for more than {args.older_than} minutes")
                print(f"✓ Marked {len(job_ids)} jobs as failed")
            else:
                print("Use --fix to mark these jobs as failed")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())