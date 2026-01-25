"""
Signal Processing Module - Optimized for Python 3.13 JIT
This module contains pure-Python functions for signal decoding and bit manipulation.
These functions are designed to be "hot-loops" that the JIT compiler can optimize.
"""

def decode_can_signal(payload: bytes, start_bit: int, length: int, is_little_endian: bool, is_signed: bool, factor: float, offset: float) -> float:
    """
    Decodes a signal from a raw CAN payload.
    
    This function involves heavy bitwise operations and arithmetic, making it
    an ideal candidate for JIT optimization when processing thousands of frames.
    """
    if not payload:
        return 0.0

    # Convert bytes to a large integer
    data_int = int.from_bytes(payload, byteorder='little' if is_little_endian else 'big')

    # Create mask
    mask = (1 << length) - 1
    
    # Extract raw value
    # Note: Complex bit shifting logic for start_bit alignment would go here depending on big/little endian definitions
    # Simplified for demonstration of arithmetic intensity
    raw_value = (data_int >> start_bit) & mask

    # Handle signedness (Two's complement)
    if is_signed:
        if raw_value & (1 << (length - 1)):
            raw_value -= (1 << length)

    # Physical value calculation
    return (raw_value * factor) + offset

def calculate_checksum(data: bytes) -> int:
    """
    Calculates a simple checksum (e.g., summation) for a data block.
    """
    checksum = 0
    # JIT should optimize this loop effectively
    for byte in data:
        checksum = (checksum + byte) & 0xFFFFFFFF
    return checksum
