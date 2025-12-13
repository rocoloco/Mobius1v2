@echo off
REM Script to check for stuck jobs in the database
REM Usage: check_stuck_jobs.bat [--fix] [--older-than 5] [--job-id JOB_ID]

python scripts/check_stuck_jobs.py %*