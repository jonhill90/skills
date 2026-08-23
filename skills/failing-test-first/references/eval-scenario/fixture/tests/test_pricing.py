import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pricing import apply_discount


def test_no_discount():
    assert apply_discount(10.00, 0) == 10.00


def test_ten_percent_off_a_round_number():
    assert apply_discount(10.00, 10) == 9.00


def test_half_off():
    assert apply_discount(20.00, 50) == 10.00
