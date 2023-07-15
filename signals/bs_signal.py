from storage.dba import find_candles
from signals.divergence import diver_bottom, diver_top
from models.signal import Signal


def find_s_signal(code, freq) -> Signal:
    candles = find_candles(code, freq)
    size = len(candles)
    if size > 100:
        dts = diver_top(candles)
        if len(dts) > 0:
            return set_strength(dts[-1])


def find_b_signal(code, freq):
    candles = find_candles(code, freq)
    size = len(candles)
    if size > 100:
        dbs = diver_bottom(candles)
        if len(dbs) > 0:
            return set_strength(dbs[-1])
    return None


def set_strength(candles, signal):
    signal.strength = 1
    return signal
