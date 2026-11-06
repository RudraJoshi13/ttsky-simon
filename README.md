![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg)

# SIMON 128/128 Bit-Serial Block Cipher (Tiny Tapeout)

Bit-serial SIMON 128/128 encryption core (OpenCores `simon_core`, unchanged) on the Tiny Tapeout pins,
with a full scan chain (281 flip-flops, 98.47% stuck-at fault coverage with 103 patterns) inserted with
Difetto and hardened in Sky130 as a custom GDS (1x2 tiles, 60 MHz).

- [Project documentation](docs/info.md)
- Licence: Apache-2.0. The SIMON core files (`src/Simon_bit_serial_*.v`) are licensed under the LGPL
  (see `src/LICENSE.simon`).
  