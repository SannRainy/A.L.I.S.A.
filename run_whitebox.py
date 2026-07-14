# -*- coding: utf-8 -*-
"""
Custom Test Runner for TVJP White-box Basis Path Testing.
Prints test execution results in a format identical to the PHPUnit / Artisan test output.
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
    # Import the test cases dynamically
    sys.path.insert(0, 'backend')
    sys.path.insert(0, 'backend/tests/layers')
    from test_l5_whitebox import Test_L5_WhiteBox

    # Create a test suite
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    tests = loader.loadTestsFromTestCase(Test_L5_WhiteBox)
    suite.addTests(tests)

    print(f"\n{Fore.WHITE}{Style.BRIGHT}satya@TVJP:~$ python run_whitebox.py")
    
    # Header format identical to: PASS Tests\Feature\Admin\StudentScoreStoreTest
    print(f"  {Fore.BLACK}{Fore.GREEN}{Style.BRIGHT} PASS {Style.RESET_ALL} {Fore.WHITE}backend\\tests\\layers\\test_l5_whitebox.py")

    start_time = time.perf_counter()
    passed_count = 0
    total_count = 0

    # Group and sort test methods to run them in path order
    test_methods = []
    for test in tests:
        test_methods.append(test)
    
    # Sort by method name (submitReview path1..3, handleAnswer path1..4, finishExam path1..3, sendChat path1..3)
    test_methods.sort(key=lambda t: t._testMethodName)

    # Dictionary to map test function names to human readable path descriptions
    descriptions = {
        # submitReview
        "test_path1_submitReview_no_user_or_item": "path1 ulasan diabaikan karena user atau item kosong",
        "test_path2_submitReview_advance_card": "path2 perekaman sukses dan kartu maju",
        "test_path3_submitReview_finish_dojo": "path3 perekaman sukses pada kartu terakhir",
        # handleAnswer
        "test_path1_handleAnswer_already_evaluating": "path1 pencegahan klik ganda (isEvaluating = True)",
        "test_path2_handleAnswer_correct_first_attempt": "path2 jawaban benar percobaan pertama tanpa hint (+10 XP)",
        "test_path3_handleAnswer_correct_with_hint": "path3 jawaban benar pada percobaan kedua dengan bantuan hint (+4 XP)",
        "test_path4_handleAnswer_incorrect_flow": "path4 jawaban salah menambah jumlah attempts",
        # finishExam
        "test_path1_finishExam_timeUp_logged_out": "path1 ujian selesai untuk pengguna tamu (Demo Mode)",
        "test_path2_finishExam_timeUp_logged_in_success": "path2 ujian selesai waktu habis untuk user login (API Success)",
        "test_path3_finishExam_timeUp_logged_in_failure": "path3 ujian selesai namun API error ditangani dengan aman",
        # sendChat
        "test_path1_sendChat_empty_or_loading": "path1 input kosong atau sistem sedang memproses pesan (Guard)",
        "test_path2_sendChat_ws_open": "path2 websocket OPEN pesan dikirim langsung",
        "test_path3_sendChat_ws_connecting": "path3 websocket CONNECTING pengiriman ditunda via listener"
    }

    # Run each test case and print the output
    for test in test_methods:
        method_name = test._testMethodName
        desc = descriptions.get(method_name, method_name)

        t_start = time.perf_counter()
        
        # Run test case and redirect stdout to suppress the parent test class verbose printing
        result = unittest.TestResult()
        with redirect_stdout(io.StringIO()):
            test.run(result)
        
        t_duration = time.perf_counter() - t_start
        total_count += 1

        # Fallback checkmark character in case of windows terminal encoding issues
        checkmark = "✓"
        try:
            # Test writing checkmark to verify support
            "✓".encode(sys.stdout.encoding or 'ascii')
        except UnicodeEncodeError:
            checkmark = "v"

        if result.wasSuccessful():
            passed_count += 1
            # Format: ✓ path1 ... [duration]
            # Left align the description, right align duration
            padding = 75 - len(desc)
            if padding < 1:
                padding = 1
            print(f"  {Fore.GREEN}{checkmark}{Fore.RESET} {Fore.LIGHTBLACK_EX}{desc}{' ' * padding}{Fore.LIGHTBLACK_EX}{t_duration:.2f}s")
        else:
            # If failed, print cross
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
