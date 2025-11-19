---
title: Getting started
parent: Hardware Design
nav_order: 3
has_children: true
---

# Getting Started with a Scalar Adder

This demo is the *hello world* of the FPGA workflow using Vitis, Vivado, and PYNQ. Specifically, we will build a toy *accelerator*, a scalar adder that adds two numbers.  The accelerator will run in the FPGA.   Obviously, this function is so simple there is no reason to use an FPGA.  However the process introduces the essential steps for hardware/software co-design and gives you a reproducible starting point for more advanced projects.

By completing this demo, you will learn how to:

* Design and synthesize a simple **Vitis IP** that performs a basic mathematical operation using an **AXI-Lite interface**
* Simulate the synthesized Vitis IP and view the **timing diagrams** in a VCD
* Create a minimal **Vivado project** that integrates the IP
* Synthesize the design to generate a **bitstream**
* Build a **PYNQ overlay** that loads the bitstream onto the FPGA board

This demo is designed to be modular, reproducible, and beginner-friendly—perfect for building intuition before diving into DMA, interrupts, or vectorized designs.

## Pre-Requirements
Prior to doing this demo, you will need to select an Ubuntu machine as the host computer, and follow the [installation instructions](../docs/installation.md) to install Vitis and Vivado and connect the FPGA board to the host computer.

Then select a directory on the host computer and clone the repository to that directory. 

## Next Steps

If you want to build the IP, add it to the Vivado project, and create the overlay, start from the begining with [building the IP in Vitis HLS](./vitis_ip.md).

Alternatively, the github repo already includes a pre-built overlay file.  So, you can just skip to [accessing the Vitis IP from PYNQ](./pynq.md).



 
