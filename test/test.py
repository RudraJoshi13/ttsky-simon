# SPDX-FileCopyrightText: © 2026 Rudra Joshi
# SPDX-License-Identifier: Apache-2.0
#
# Tests for tt_um_rj_simon (bit-serial SIMON 128/128).
# Expected results come from the golden model model/simon128.py, which is
# itself checked against the test vector in the SIMON paper.
#
# Pins: ui_in[0] = data_in, ui_in[2:1] = data_rdy, uo_out[0] = cipher_out.
# Inputs change on the falling edge of clk; outputs are read just before the
# next rising edge.

import os
import random
import sys

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "model"))
import simon128  # noqa: E402

IDLE, LOAD_PT, LOAD_KEY, RUN = 0, 1, 2, 3
RUN_CLOCKS = 68 * 64  # 68 rounds, 64 clocks per round

# Test vector from the SIMON paper (SIMON 128/128)
PAPER_KEY = 0x0F0E0D0C0B0A09080706050403020100
PAPER_PT = 0x63736564207372656C6C657661727420
PAPER_CT = 0x49681B1E1E54FE3F65AA832AF84E0BBC


def set_inputs(dut, data_rdy, data_in=0):
    dut.ui_in.value = (data_rdy << 1) | data_in


async def start(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())  # 50 MHz
    dut.ena.value = 1
    dut.uio_in.value = 0
    dut.rst_n.value = 1
    set_inputs(dut, IDLE)
    await FallingEdge(dut.clk)
    await FallingEdge(dut.clk)


async def encrypt(dut, plaintext, key):
    """Load plaintext and key bit-serially, run, and collect the ciphertext."""
    # load plaintext, LSB first, one bit per clock
    for i in range(128):
        set_inputs(dut, LOAD_PT, (plaintext >> i) & 1)
        await FallingEdge(dut.clk)
    # load key, LSB first
    for i in range(128):
        set_inputs(dut, LOAD_KEY, (key >> i) & 1)
        await FallingEdge(dut.clk)
    # one idle clock, then run
    set_inputs(dut, IDLE)
    await FallingEdge(dut.clk)
    set_inputs(dut, RUN)
    ct = 0
    for i in range(RUN_CLOCKS):
        await Timer(1, unit="ns")
        assert dut.uio_oe.value.to_unsigned() == 0, "uio_oe must stay 0"
        assert dut.uo_out.value.to_unsigned() >> 1 == 0, "uo_out[7:1] must stay 0"
        if i >= RUN_CLOCKS - 128:  # ciphertext appears in the last 128 clocks
            ct |= (dut.uo_out.value.to_unsigned() & 1) << (i - (RUN_CLOCKS - 128))
        await FallingEdge(dut.clk)
    set_inputs(dut, IDLE)
    await FallingEdge(dut.clk)
    return ct


@cocotb.test()
async def test_paper_vector(dut):
    """The SIMON 128/128 test vector from the designers' paper."""
    assert simon128.encrypt(PAPER_PT, PAPER_KEY) == PAPER_CT, "golden model is wrong"
    await start(dut)
    ct = await encrypt(dut, PAPER_PT, PAPER_KEY)
    assert ct == PAPER_CT, f"got {ct:032x}, expected {PAPER_CT:032x}"
    dut._log.info(f"paper vector: ciphertext {ct:032x}")


@cocotb.test()
async def test_random_vectors(dut):
    """Random plaintexts and keys, back to back, compared with the model."""
    await start(dut)
    rng = random.Random(2026)
    for n in range(5):
        pt, key = rng.getrandbits(128), rng.getrandbits(128)
        ct = await encrypt(dut, pt, key)
        exp = simon128.encrypt(pt, key)
        assert ct == exp, f"vector {n}: pt={pt:032x} key={key:032x} got {ct:032x} expected {exp:032x}"
    dut._log.info("5 random vectors match the model")
