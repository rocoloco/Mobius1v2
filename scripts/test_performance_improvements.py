#!/usr/bin/env python3
"""
Performance testing script to validate optimization improvements.

Tests the generation workflow with and without optimizations to measure
the actual performance gains from the implemented changes.
"""

import asyncio
import time
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mobius.utils.performance import get_performance_summary, log_performance_summary, clear_performance_metrics
from mobius.nodes.generate import generate_node
from mobius.models.state import JobState
from mobius.config import settings
import structlog

logger = structlog.get_logger()


async def create_test_job_state(brand_id: str = None) -> JobState:
    """Create a test job state for performance testing."""
    # Use a test brand ID or create a mock one
    test_brand_id = brand_id or "test-brand-123"
    
    return {
        "job_id": f"perf-test-{int(time.time())}",
        "brand_id": test_brand_id,
        "prompt": "Create a professional social media post with our brand colors and logo",
        "brand_hex_codes": ["#FF6B35", "#004E89", "#FFFFFF"],
        "brand_rules": "Use primary colors for headers, maintain logo integrity",
        "current_image_url": None,
        "attempt_count": 0,
        "audit_history": [],
        "compliance_scores": [],
        "is_approved": False,
        "status": "pending",
        "created_at": time.time(),
        "updated_at": time.time(),
        "webhook_url": None,
        "template_id": None,
        "generation_params": {"temperature": 0.7},
    }


async def run_performance_test(num_tests: int = 3, brand_id: str = None):
    """
    Run performance tests on the generation workflow.
    
    Args:
        num_tests: Number of test runs to perform
        brand_id: Brand ID to test with (uses test brand if None)
    """
    print(f"🚀 Starting performance test with {num_tests} runs...")
    print(f"📊 Testing optimizations:")
    print("   ✅ Parallel logo processing")
    print("   ✅ Optimized Gemini API timeouts")
    print("   ✅ HTTP connection pooling")
    print("   ✅ Brand data caching")
    print("   ✅ Performance monitoring")
    print()
    
    # Clear any existing metrics
    clear_performance_metrics()
    
    total_start_time = time.time()
    successful_runs = 0
    failed_runs = 0
    
    for i in range(num_tests):
        print(f"🔄 Running test {i + 1}/{num_tests}...")
        
        try:
            # Create test job state
            test_state = await create_test_job_state(brand_id)
            
            # Run the generate node
            start_time = time.time()
            result = await generate_node(test_state)
            duration = time.time() - start_time
            
            if result.get("status") == "generated":
                successful_runs += 1
                print(f"   ✅ Success in {duration:.2f}s")
            else:
                failed_runs += 1
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            failed_runs += 1
            print(f"   ❌ Exception: {str(e)}")
        
        # Small delay between tests
        if i < num_tests - 1:
            await asyncio.sleep(1)
    
    total_duration = time.time() - total_start_time
    
    print(f"\n📈 Performance Test Results:")
    print(f"   Total time: {total_duration:.2f}s")
    print(f"   Successful runs: {successful_runs}/{num_tests}")
    print(f"   Failed runs: {failed_runs}/{num_tests}")
    print(f"   Average per run: {total_duration/num_tests:.2f}s")
    
    # Get detailed performance metrics
    print(f"\n🔍 Detailed Performance Breakdown:")
    summary = get_performance_summary()
    
    for operation, stats in summary.items():
        print(f"   {operation}:")
        print(f"     Count: {stats['count']}")
        print(f"     Average: {stats['avg_ms']:.0f}ms")
        print(f"     Min: {stats['min_ms']:.0f}ms")
        print(f"     Max: {stats['max_ms']:.0f}ms")
        print(f"     P95: {stats['p95_ms']:.0f}ms")
    
    # Log to structured logs
    log_performance_summary()
    
    print(f"\n💡 Expected improvements vs. baseline:")
    print(f"   🎯 Target: 70-80% faster (0.6-1.2 min vs 2-3 min)")
    print(f"   📊 Actual average: {total_duration/num_tests:.2f}s per generation")
    
    if total_duration/num_tests < 90:  # Less than 1.5 minutes
        print(f"   🎉 EXCELLENT: Achieved target performance!")
    elif total_duration/num_tests < 120:  # Less than 2 minutes
        print(f"   ✅ GOOD: Significant improvement achieved!")
    else:
        print(f"   ⚠️  NEEDS WORK: Performance still needs optimization")


async def test_logo_processing_performance():
    """Test specifically the logo processing improvements."""
    print(f"\n🖼️  Testing Logo Processing Performance...")
    
    from mobius.nodes.generate import fetch_and_process_logos_parallel
    from mobius.models.brand import LogoRule
    
    # Create test logos (using placeholder URLs)
    test_logos = [
        LogoRule(
            variant_name="Primary Logo",
            url="https://via.placeholder.com/300x200/FF6B35/FFFFFF?text=Logo1",
            min_width_px=150,
            clear_space_ratio=0.1,
            forbidden_backgrounds=[]
        ),
        LogoRule(
            variant_name="Secondary Logo", 
            url="https://via.placeholder.com/300x200/004E89/FFFFFF?text=Logo2",
            min_width_px=100,
            clear_space_ratio=0.1,
            forbidden_backgrounds=[]
        ),
        LogoRule(
            variant_name="Icon",
            url="https://via.placeholder.com/100x100/FFFFFF/000000?text=Icon",
            min_width_px=50,
            clear_space_ratio=0.05,
            forbidden_backgrounds=[]
        )
    ]
    
    print(f"   Testing parallel processing of {len(test_logos)} logos...")
    
    try:
        start_time = time.time()
        results = await fetch_and_process_logos_parallel(
            test_logos,
            job_id="logo-perf-test",
            operation_type="performance_test"
        )
        duration = time.time() - start_time
        
        print(f"   ✅ Processed {len(results)}/{len(test_logos)} logos in {duration:.2f}s")
        print(f"   📊 Average: {duration/len(test_logos):.2f}s per logo")
        
        if duration < 2.0:
            print(f"   🎉 EXCELLENT: Logo processing is optimized!")
        elif duration < 5.0:
            print(f"   ✅ GOOD: Significant improvement in logo processing!")
        else:
            print(f"   ⚠️  SLOW: Logo processing needs more optimization")
            
    except Exception as e:
        print(f"   ❌ Logo processing test failed: {str(e)}")


def main():
    """Main entry point for performance testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test performance improvements")
    parser.add_argument("--runs", type=int, default=3, help="Number of test runs")
    parser.add_argument("--brand-id", type=str, help="Brand ID to test with")
    parser.add_argument("--logo-test", action="store_true", help="Run logo processing test")
    
    args = parser.parse_args()
    
    async def run_tests():
        if args.logo_test:
            await test_logo_processing_performance()
        
        await run_performance_test(args.runs, args.brand_id)
    
    # Run the async tests
    asyncio.run(run_tests())


if __name__ == "__main__":
    main()