import os

# Create a 16KB mock binary
size = 0x4000
data = bytearray(size)

# Fill 0x2000 with a 16x16 gradient (Fuel Map)
# Values 0..255
for r in range(16):
    for c in range(16):
        val = (r * 16) + c
        data[0x2000 + (r*16) + c] = val # Linear gradient

# Fill 0x3000 with a "Peak" (Spark Map)
for r in range(8):
    for c in range(8):
        # Center peak
        dist = ((r-3.5)**2 + (c-3.5)**2)
        val = int(max(0, 255 - (dist * 10)))
        data[0x3000 + (r*8) + c] = val

with open('e:\\Programming\\CANdy_Diag_Pro\\mock_ecu.bin', 'wb') as f:
    f.write(data)
