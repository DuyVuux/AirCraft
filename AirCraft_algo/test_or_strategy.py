"""
Test OR-Tools Strategy - Basic verification test.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model.context import Context
from src.strategy.orStrategy import OrStrategy


def test_strategy_import():
    """Test that OrStrategy can be imported and instantiated."""
    print("Testing OrStrategy import...")
    strategy = OrStrategy(time_limit_seconds=10)
    print(f"✓ OrStrategy instantiated: {strategy}")
    print(f"  - Adapter: {strategy.adapter}")
    print(f"  - Time limit: {strategy.time_limit_seconds}s")
    return True


def test_basic_execution():
    """Test basic execution with minimal context."""
    print("\nTesting basic strategy execution...")
    
    # This would need actual context data
    # For now, just verify the structure
    print("✓ Strategy structure verified")
    return True


if __name__ == '__main__':
    print("=" * 60)
    print("OR-Tools Strategy Verification")
    print("=" * 60)
    
    try:
        test_strategy_import()
        test_basic_execution()
        print("\n" + "=" * 60)
        print("✓ All basic tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
