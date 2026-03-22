"""Test runner for toy key-value store and other simple tasks."""

import subprocess
import tempfile
import os
import sys
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class TestResult:
    """Result of a single test case."""
    name: str
    passed: bool
    input_data: Any
    expected: Any
    actual: Any
    error_message: str = ""
    execution_time_ms: float = 0.0


class TestsRunner:
    """Test runner for pre-defined tests."""
    
    def __init__(self, code_runner: Optional[Any] = None):
        self.code_runner = code_runner
        self.results: List[TestResult] = []
    
    def run_kv_store_tests(self, implementation_code: str) -> Dict[str, Any]:
        test_harness = self._create_kv_test_harness(implementation_code)
        return self._execute_tests(test_harness, "kv_store")
    
    def _create_kv_test_harness(self, impl_code: str) -> str:
        return f"""
{impl_code}

import time
import sys

def run_tests():
    results = []
    
    def test(name, test_fn):
        start = time.time()
        try:
            test_fn()
            elapsed = (time.time() - start) * 1000
            results.append({{"name": name, "passed": True, "error": "", "time_ms": elapsed}})
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            results.append({{"name": name, "passed": False, "error": str(e), "time_ms": elapsed}})
    
    def test_basic_put_get():
        store = KVStore()
        store.put("key1", "value1")
        assert store.get("key1") == "value1", "Basic get failed"
    test("basic_put_get", test_basic_put_get)
    
    def test_update():
        store = KVStore()
        store.put("key1", "value1")
        store.put("key1", "value2")
        assert store.get("key1") == "value2", "Update failed"
    test("update_existing", test_update)
    
    def test_delete():
        store = KVStore()
        store.put("key1", "value1")
        store.delete("key1")
        assert store.get("key1") is None, "Delete failed"
    test("delete_key", test_delete)
    
    def test_get_missing():
        store = KVStore()
        result = store.get("nonexistent")
        assert result is None, "Get non-existent should return None"
    test("get_nonexistent", test_get_missing)
    
    def test_delete_missing():
        store = KVStore()
        store.delete("nonexistent")
    test("delete_nonexistent", test_delete_missing)
    
    def test_empty_key():
        store = KVStore()
        store.put("", "value")
        assert store.get("") == "value", "Empty key failed"
    test("empty_string_key", test_empty_key)
    
    def test_multiple_keys():
        store = KVStore()
        for i in range(100):
            store.put(f"key_{{i}}", f"value_{{i}}")
        for i in range(100):
            assert store.get(f"key_{{i}}") == f"value_{{i}}"
    test("multiple_keys", test_multiple_keys)
    
    import json
    print("TEST_RESULTS_START")
    print(json.dumps(results))
    print("TEST_RESULTS_END")

if __name__ == "__main__":
    run_tests()
"""
    
    def _execute_tests(self, test_code: str, suite_name: str) -> Dict[str, Any]:
        temp_file = None
        results = {
            "suite": suite_name,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": [],
            "success": False
        }
        
        try:
            with tempfile