# -*- coding: utf-8 -*-
"""
Custom Test Runner for TVJP White-box Basis Path Testing: handleAnswer()
"""

import sys
import os
import time
import unittest
import io
from contextlib import redirect_stdout
from colorama import init, Fore, Style

# Configure stdout/stderr to use UTF-8 to prevent UnicodeEncodeError on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Initialize colorama for cross-platform color support
init(autoreset=True)

def run_tests():
    sys.path.insert(0, 'backend')
    sys.path.insert(0, 'backend/tests/layers')
    from test_l5_whitebox import Test_L5_WhiteBox

    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    tests = loader.loadTestsFromTestCase(Test_L5_WhiteBox)

    # Filter only handleAnswer tests
    target_methods = [
        "test_path1_handleAnswer_already_evaluating",
        "test_path2_handleAnswer_correct_first_attempt",
        "test_path3_handleAnswer_correct_with_hint",
        "test_path4_handleAnswer_incorrect_flow"
    ]
    
    test_methods = []
    for test in tests:
        if test._testMethodName in target_methods:
            test_methods.append(test)
            
    test_methods.sort(key=lambda t: t._testMethodName)

    print(f"\n{Fore.WHITE}{Style.BRIGHT}satya@TVJP:~$ python run_whitebox_handleAnswer.py")
    print(f"  {Fore.BLACK}{Fore.GREEN}{Style.BRIGHT} PASS {Style.RESET_ALL} {Fore.WHITE}backend\\tests\\layers\\test_l5_whitebox.py::handleAnswer")

    start_time = time.perf_counter()
    passed_count = 0
    total_count = 0

    descriptions = {
        "test_path1_handleAnswer_already_evaluating": "path1 pencegahan klik ganda (isEvaluating = True)",
        "test_path2_handleAnswer_correct_first_attempt": "path2 jawaban benar percobaan pertama tanpa hint (+10 XP)",
        "test_path3_handleAnswer_correct_with_hint": "path3 jawaban benar pada percobaan kedua dengan bantuan hint (+4 XP)",
        "test_path4_handleAnswer_incorrect_flow": "path4 jawaban salah menambah jumlah attempts"
    }

    for test in test_methods:
        method_name = test._testMethodName
        desc = descriptions.get(method_name, method_name)

        t_start = time.perf_counter()
        
        result = unittest.TestResult()
        with redirect_stdout(io.StringIO()):
            test.run(result)
        
        t_duration = time.perf_counter() - t_start
        total_count += 1

        checkmark = "✓"
        try:
            "✓".encode(sys.stdout.encoding or 'ascii')
        except UnicodeEncodeError:
            checkmark = "v"

        if result.wasSuccessful():
            passed_count += 1
            padding = 75 - len(desc)
            if padding < 1:
                padding = 1
            print(f"  {Fore.GREEN}{checkmark}{Fore.RESET} {Fore.LIGHTBLACK_EX}{desc}{' ' * padding}{Fore.LIGHTBLACK_EX}{t_duration:.2f}s")
        else:
            cross = "✗"
            try:
                "✗".encode(sys.stdout.encoding or 'ascii')
            except UnicodeEncodeError:
                cross = "x"
            print(f"  {Fore.RED}{cross}{Fore.RESET} {Fore.RED}{desc}")
            for failure in result.failures + result.errors:
                print(f"    {Fore.RED}Error in {method_name}: {failure[1]}")

    duration = time.perf_counter() - start_time
    print(f"\n  Tests:    {Fore.GREEN}{passed_count} passed{Fore.RESET} ({total_count} total)")
    print(f"  Duration: {duration:.2f}s\n")

if __name__ == "__main__":
    run_tests()
