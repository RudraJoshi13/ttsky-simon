/*
 * Copyright (c) 2026 Rudra Joshi
 * SPDX-License-Identifier: Apache-2.0
 *
 * Tiny Tapeout wrapper for the bit-serial SIMON 128/128 core from
 * opencores.org/projects/simon_core (Virginia Tech SES Lab, Ege Gulcan).
 * The three core files are used unchanged; this file only connects the
 * core's ports to the Tiny Tapeout pins. No logic is added.
 *
 * Pins:
 *   ui_in[0]     data_in: plaintext or key bit, one bit per clock, LSB first
 *   ui_in[2:1]   data_rdy: 0 = idle/reset, 1 = load plaintext,
 *                2 = load key, 3 = run
 *   uo_out[0]    cipher_out: ciphertext bit, valid during the last 128
 *                clocks of the 4352-clock run, LSB first
 */

`default_nettype none
`timescale 1ns / 1ps

module tt_um_rj_simon (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  wire cipher_out;

  top_module simon (
      .clk       (clk),
      .data_in   (ui_in[0]),
      .data_rdy  (ui_in[2:1]),
      .cipher_out(cipher_out)
  );

  assign uo_out  = {7'b0000000, cipher_out};
  assign uio_out = 8'h00;
  assign uio_oe  = 8'h00;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, rst_n, ui_in[7:3], uio_in, 1'b0};

endmodule
