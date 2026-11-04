#!/usr/bin/env python3
"""Legacy libhwbinder source regression; not a runtime IPC or Soong test."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def check(ok, message):
    if not ok:
        raise AssertionError(message)
    print("PASS historical source:", message)


try:
    bp = (ROOT / "Android.bp").read_text()
    state = (ROOT / "ProcessState.cpp").read_text()
    parcel = (ROOT / "Parcel.cpp").read_text()
    for name in ('name: "libhwbinder_headers"', 'name: "libhwbinder"',
                 'name: "libhwbinder-impl-internal"', 'name: "hwbinder_lto"'):
        check(name in bp, name)
    check('name: "libhwbinder-impl-internal"' in bp
          and 'recovery_available: true' in bp, "old IPC static implementation and recovery exposure")
    check("ProcessState::setThreadPoolConfiguration" in state
          and "mThreadPoolStarted && maxThreads < mMaxThreads" not in state,
          "old PE disabled threadpool shrink rejection, NOT PORTED")
    check("parent >= mObjectsSize" in parcel
          and "Parent index %zu but only have %zu objects" in parcel,
          "old Parcel parent bounds check preserved")
    check('"/dev/hwbinder"' in state, "HIDL binder driver path used")
    print("PASS: legacy source checks only; not Android17 or mondrian behavior.")
except (AssertionError, OSError) as exc:
    print("FAIL:", exc, file=sys.stderr)
    sys.exit(1)
