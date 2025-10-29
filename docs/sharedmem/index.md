---
title: Shared Memory PS Interface
parent: FPGA Demos
nav_order: 4
has_children: true
---

# Shared Memory Interface to the Processor

In the previous unit on [loop optimization]({site.root}/fpgademos/loopopt), we built and optimized a simple vector multiplier IP core.
We will now interconnect this IP to the PS.   In this unit, we consider a simple interconnection method based on shared memory.

We will create two options:

* Shared DDR memory:  PS and and PL share DDR memory.
   * This option has virtually unlimiited data
   * But access is slower since we are going out of the FPGA 
   * Also, the interface to the memory will content with the PS accesses to the data


## Understanding AXI and Memory Transfers

### What is AXI?

[AXI (Advanced eXtensible Interface)](https://adaptivesupport.amd.com/s/article/1053914) is a standard protocol used in FPGA and SoC designs to connect different components like processors, memory, and custom IP blocks. It defines how data is transferred between these components in a fast and flexible way.

There are different types of AXI interfaces:
- **AXI4**: For high-performance memory-mapped transfers
- **AXI4-Lite**: For simple control/status registers
- **AXI4-Stream**: For continuous data streams (e.g., audio, video, FFT)

---

### Master and Slave Roles

In AXI, every transaction involves two roles:
- **Master**: Initiates the read or write operation
- **Slave**: Responds to the request

For example:
- The **Processing System (PS)** is a master when it reads/writes to memory.
- A custom **Vitis HLS IP** with `m_axi` ports is also a master — it initiates memory reads/writes.
- The **DDR memory** is a slave — it responds to read/write requests from either the PS or the IP.

---

### What We’re Doing in This Unit

In this unit, we explore a simple memory transfer:
- Either the **PS** or a **custom IP** acts as the **master**
- The **memory (DDR)** acts as the **slave**
- The master reads input data from memory, performs computation, and writes results back

---

### Don’t Worry — Vivado Makes It Easy

Vivado’s **Block Design** environment makes it easy to:
- Instantiate IP blocks (like your custom vector multiplier)
- Connect AXI interfaces with drag-and-drop wiring
- Automatically generate address maps and interconnects

You’ll be able to build powerful hardware/software systems without writing low-level HDL — and still understand what’s happening under the hood.

---

Go to [Building the Vivado project](./vivado.md).


