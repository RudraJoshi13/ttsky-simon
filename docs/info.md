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
| `uo[0]` | `cipher_out`: ciphertext bit, least significant bit first |

All other pins are unused. `uo[7:1]` read 0 and all `uio` pins are inputs.

## How to test

All inputs are sampled on the rising edge of `clk`. Change them away from the rising edge.

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

## Clock

Use a clock of 60 MHz or lower. Tiny Tapeout expects the highest usable clock to be about 66 MHz, set by the
I/O pads ([tinytapeout.com/specs/clock](https://www.tinytapeout.com/specs/clock/)), so 60 MHz leaves a margin.

The layout was checked by static timing analysis at 125 MHz (8 ns clock period). It met setup and hold timing
at all nine process, voltage and temperature corners. The worst setup slack was 0.6967 ns and the worst hold
slack was 0.0996 ns.

## External hardware

None. The RP2040 on the Tiny Tapeout demo board can drive `ui[2:0]` and read `uo[0]`.
