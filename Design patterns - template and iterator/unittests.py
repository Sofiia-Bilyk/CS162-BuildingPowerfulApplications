"""
Unit Testing Framework using the Template Design Pattern
--------------------------------------------------------
The base class TestCase defines the template method `run()`, which outlines
the full test lifecycle: setUp → test method → tearDown → report result.
Subclasses only override setUp, tearDown, and the individual test methods.
"""

import traceback
import sys
import os
import time 

# Allow importing ClockIterator without running the infinite loop at module level
sys.path.insert(0, os.path.dirname(__file__))


# ---------------------------------------------------------------------------
# Testing Framework
# ---------------------------------------------------------------------------

class TestCase:
    """
    Base class for all test cases — implements the Template Method pattern.

    Template method: run()
      1. setUp()      — prepare state before the test (hook, override if needed)
      2. test method  — the actual assertion logic (defined in subclass)
      3. tearDown()   — clean up after the test (hook, override if needed)
    """

    def setUp(self):
        """Hook: runs before every test method. Override to set up fixtures."""
        pass

    def tearDown(self):
        """Hook: runs after every test method. Override to clean up."""
        pass

    def run(self, test_name):
        """
        Template method: defines the skeleton of a single test execution.
        Subclasses must NOT override this — they override setUp/tearDown/tests.
        """
        self.setUp()
        try:
            getattr(self, test_name)()
            print(f"  PASS  {test_name}")
            return True
        except AssertionError as e:
            print(f"  FAIL  {test_name}: {e}")
            return False
        except Exception as e:
            print(f"  ERROR {test_name}: {e}")
            traceback.print_exc()
            return False
        finally:
            self.tearDown()

    # --- Assertion helpers --------------------------------------------------

    def assertEqual(self, first, second, msg=None):
        if first != second:
            raise AssertionError(msg or f"{first!r} != {second!r}")

    def assertNotEqual(self, first, second, msg=None):
        if first == second:
            raise AssertionError(msg or f"Expected values to differ, got {first!r}")

    def assertTrue(self, expr, msg=None):
        if not expr:
            raise AssertionError(msg or f"Expected True, got {expr!r}")

    def assertFalse(self, expr, msg=None):
        if expr:
            raise AssertionError(msg or f"Expected False, got {expr!r}")

    def assertIn(self, member, container, msg=None):
        if member not in container:
            raise AssertionError(msg or f"{member!r} not found in {container!r}")


class TestRunner:
    """Discovers and runs all test_* methods on a TestCase subclass."""

    def run(self, test_case_class):
        instance = test_case_class()
        test_methods = [m for m in dir(instance) if m.startswith("test_")]
        print(f"\nRunning {test_case_class.__name__} ({len(test_methods)} tests)")
        print("-" * 50)
        passed = sum(instance.run(name) for name in test_methods)
        failed = len(test_methods) - passed
        print("-" * 50)
        print(f"Results: {passed} passed, {failed} failed\n")
        return failed == 0


# ---------------------------------------------------------------------------
# Tests for ClockIterator
# ---------------------------------------------------------------------------

# Import only the class, not the runaway infinite loop at module bottom.
# We re-define ClockIterator here by importing only the class definition.
import ast, types

def _import_clock():
    """Load ClockIterator without executing the infinite loop at file bottom.

    Uses the ast module to extract only the ClassDef node, so no module-level
    statements (the infinite for loop, imports, etc.) are ever executed.
    """
    source_path = os.path.join(os.path.dirname(__file__), "InfiniteClock.py")
    with open(source_path) as f:
        source = f.read()
    tree = ast.parse(source)
    # Keep only class definitions — drop everything else (for loop, assignments…)
    # Keep imports and class definitions; drop module-level statements that
    # start the infinite loop (For nodes, Assign to 'clock', bare Expr calls).
    tree.body = [
        node for node in tree.body
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.ClassDef))
    ]
    ast.fix_missing_locations(tree)
    module = types.ModuleType("InfiniteClock")
    exec(compile(tree, source_path, "exec"), module.__dict__)
    return module.ClockIterator

ClockIterator = _import_clock()


class TestClockIterator(TestCase):

    def setUp(self):
        """Create a fresh ClockIterator before each test."""
        self.clock = ClockIterator()

    # --- Structural tests ---------------------------------------------------

    def test_is_iterable(self):
        """ClockIterator should return itself from __iter__."""
        self.assertEqual(iter(self.clock), self.clock)

    def test_has_next(self):
        """__next__ should return a value without raising StopIteration."""
        result = next(self.clock)
        self.assertTrue(result is not None)

    # --- Format tests -------------------------------------------------------

    def test_first_value_is_midnight(self):
        """First value produced should be 00:00."""
        self.assertEqual(next(self.clock), "00:00")

    def test_second_value_is_00_01(self):
        """Second value should be 00:01."""
        next(self.clock)
        self.assertEqual(next(self.clock), "00:01")

    def test_format_has_colon(self):
        """Output should contain a colon separating hours and minutes."""
        value = next(self.clock)
        self.assertIn(":", value)

    def test_format_length(self):
        """Each time string should be exactly 5 characters (HH:MM)."""
        value = next(self.clock)
        self.assertEqual(len(value), 5)

    def test_zero_padding_hours(self):
        """Hours below 10 should be zero-padded (e.g. 00, 01)."""
        value = next(self.clock)          # 00:00
        self.assertEqual(value[:2], "00")

    def test_zero_padding_minutes(self):
        """Minutes below 10 should be zero-padded (e.g. 00, 05)."""
        value = next(self.clock)          # 00:00
        self.assertEqual(value[3:], "00")

    # --- Progression tests --------------------------------------------------

    def test_minute_rollover(self):
        """After 00:59 the next value should be 01:00."""
        for _ in range(60):               # advance to 01:00
            next(self.clock)
        self.assertEqual(next(self.clock), "01:00")

    def test_last_value_before_midnight(self):
        """The 1440th value (index 1439) should be 23:59."""
        for _ in range(1439):
            next(self.clock)
        self.assertEqual(next(self.clock), "23:59")

    def test_wraps_back_to_midnight(self):
        """After 23:59 the clock should wrap back to 00:00."""
        for _ in range(1440):             # exhaust a full day
            next(self.clock)
        self.assertEqual(next(self.clock), "00:00")

    def test_sequence_of_first_five(self):
        """First five values should be 00:00 through 00:04."""
        expected = ["00:00", "00:01", "00:02", "00:03", "00:04"]
        actual = [next(self.clock) for _ in range(5)]
        self.assertEqual(actual, expected)

    def test_infinite_no_stop_iteration(self):
        """Iterator should never raise StopIteration over multiple full days."""
        try:
            for _ in range(1440 * 3):     # three full days
                next(self.clock)
            self.assertTrue(True)
        except StopIteration:
            raise AssertionError("ClockIterator raised StopIteration unexpectedly")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    runner = TestRunner()
    all_passed = runner.run(TestClockIterator)
    sys.exit(0 if all_passed else 1)
