"""
API endpoints for testing and evaluation of the personal finance advisor system.
"""
from fastapi import APIRouter, Depends
from app.services.testing_framework import testing_framework
from app.utils.auth import get_current_user
from typing import Dict

router = APIRouter()

@router.get("/run-tests")
async def run_comprehensive_tests(user=Depends(get_current_user)):
    """Run comprehensive test suite (admin only)."""
    # In production, this should be restricted to admin users
    test_results = await testing_framework.run_comprehensive_tests()
    return test_results

@router.get("/test-report")
async def generate_test_report(user=Depends(get_current_user)):
    """Generate comprehensive test report for documentation."""
    report = await testing_framework.generate_test_report()
    return report

@router.get("/performance-tests")
async def run_performance_tests(user=Depends(get_current_user)):
    """Run performance tests only."""
    performance_results = await testing_framework._run_performance_tests()
    return performance_results

@router.get("/accuracy-tests")
async def run_accuracy_tests(user=Depends(get_current_user)):
    """Run accuracy tests only."""
    accuracy_results = await testing_framework._run_accuracy_tests()
    return accuracy_results
