<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This project puts the SIMON 128/128 block cipher (128-bit block, 128-bit key, 68 rounds) on Tiny Tapeout. SIMON
was designed by Beaulieu et al. ("The SIMON and SPECK Families of Lightweight Block Ciphers", 2013).

The core is the bit-serial SIMON implementation from [opencores.org/projects/simon_core](https://opencores.org/projects/simon_core)
(Virginia Tech Secure Embedded Systems Lab, Ege Gulcan; described in A. Aysu, E. Gulcan and P. Schaumont, "SIMON
Says: Break Area Records of Block Ciphers on FPGAs", IEEE Embedded Systems Letters, 2014). The core files are used
unchanged. They process one bit per clock cycle, which keeps the design very small. The project's top module only
connects the core's four ports to the Tiny Tapeout pins.

| Pin | Function |
|-----|----------|
| `ui[0]` | `data_in`: plaintext or key bit, one bit per clock, least significant bit first |
| `ui[2:1]` | `data_rdy`: 0 = idle (resets the counters), 1 = load plaintext, 2 = load key, 3 = run |
| `ui[3]` | `scan_en`: scan enable, keep 0 in normal use (see Scan chain test) |
| `ui[4]` | `scan_in`: scan chain input |
| `uo[0]` | `cipher_out`: ciphertext bit, least significant bit first |
| `uo[1]` | `scan_out`: scan chain output |

All other pins are unused. `uo[7:2]` read 0 and all `uio` pins are inputs. `uo[1]` shows the last
flip-flop of the scan chain, so it also changes during normal use; ignore it unless you run the scan test.

## How to test

All inputs are sampled on the rising edge of `clk`. Change them away from the rising edge. Keep `ui[3]`
(scan enable) low.

1. Set `data_rdy` to 0 for at least one clock.
2. Set `data_rdy` to 1 and shift in the 128 plaintext bits on `ui[0]`, bit 0 first, one bit per clock.
3. Set `data_rdy` to 2 and shift in the 128 key bits, bit 0 first, one bit per clock.
4. Set `data_rdy` to 0 for one clock.
5. Set `data_rdy` to 3 and keep it there for 4352 clocks (68 rounds of 64 clocks).
6. During the last 128 of those clocks, `uo[0]` gives the ciphertext, bit 0 first. Read it before each rising edge.
7. Set `data_rdy` back to 0.

The core has no done flag, so the controller (for example the RP2040 on the demo board) must count the clocks.

Test vector from the SIMON paper:

| Plaintext | Key | Ciphertext |
|-----------|-----|------------|
| `63736564207372656c6c657661727420` | `0f0e0d0c0b0a09080706050403020100` | `49681b1e1e54fe3f65aa832af84e0bbc` |

## Scan chain test

The design also contains a scan chain for manufacturing test (design for test). It was inserted with
Difetto (OpenROAD scan insertion with placement-aware chain ordering), so the layout is hardened locally
and submitted as a custom GDS. The SIMON core files are unchanged; the scan flip-flops replace the normal
flip-flops after synthesis. All 281 flip-flops are in one chain. The chain is shifted on the normal clock
`clk`. Scan in is `ui[4]`, scan out is `uo[1]`, and scan enable is `ui[3]`.

One test pattern is applied as follows:

1. Set `ui[3]` high.
2. Shift the 281 flip-flop values in on `ui[4]`, one per rising clock edge.
3. Set `ui[3]` low and set the other `ui` inputs from the pattern. Check `uo[7:0]` against the expected
   values. `uo[1]` shows the value just loaded into the last flip-flop of the chain.
4. Give one clock (the capture clock).
5. Set `ui[3]` high and shift the 281 captured values out on `uo[1]` while the next pattern shifts in.

The test patterns were generated with quaigh: 103 patterns give 98.47% coverage of single stuck-at
faults (2,706 of 2,748 collapsed faults). This number covers the logic after scan insertion; it does not
include delay faults or the buffers added later during placement and routing. The chain itself is checked
separately by shifting a known bit stream through it. All 103 patterns were replayed on the final routed
gate-level netlist in simulation with no mismatches.

## Clock

Use a clock of 60 MHz or lower. Tiny Tapeout expects the highest usable clock to be about 66 MHz, set by the
I/O pads ([tinytapeout.com/specs/clock](https://www.tinytapeout.com/specs/clock/)), so 60 MHz leaves a margin.

The layout was checked by static timing analysis at 125 MHz (8 ns clock period). It met setup and hold timing
at all nine process, voltage and temperature corners. The worst setup slack was 0.7463 ns and the worst hold
slack was 0.0605 ns.

## External hardware

None. The RP2040 on the Tiny Tapeout demo board can drive `ui[4:0]` and read `uo[1:0]`.
