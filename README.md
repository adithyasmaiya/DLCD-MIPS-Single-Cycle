# Single-Cycle MIPS Datapath — DLCD Mini Project

## Project Overview
This project implements an educational single-cycle MIPS architectural
model, a control-unit signal model, execution-trace generation, and an
interactive datapath viewer. A separate gem5 experiment is included as
a reference simulation.

## Main Components
- Python single-cycle MIPS simulator
- Instruction execution and register/memory state
- Control-unit verification
- Execution trace and CSV generation
- Datapath visualization
- gem5 reference experiment
- Project report and simulation comparison

## Supported Instructions
ADDI, ADD, SUB, AND, OR, SLT, LW, SW, BEQ, J

## Running the Simulator
From the project root:

    python3 src/mips_simulator.py

## Running Tests
    python3 tests/verify_mips.py
    python3 tests/test_control_unit.py

Run additional tests when their files are present.

## Generating the Datapath Viewer
    python3 src/generate_datapath_view.py

Open results/datapath_view.html in a browser.

## Limitations
The Python model is an educational architectural model.
The gem5 experiment uses the configured gem5 CPU model and does
not implement a custom single-cycle CPU inside gem5.
