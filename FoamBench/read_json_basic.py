#!/usr/bin/env python3
"""Backward-compatible wrapper: unpack the Basic split (see read_json.py)."""

import sys

import read_json

if __name__ == "__main__":
    sys.argv = [sys.argv[0], "--split", "basic"] + sys.argv[1:]
    sys.exit(read_json.main())
