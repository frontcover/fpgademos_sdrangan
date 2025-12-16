---
title: C and RTL Simulation
parent: Command-Response FIFO Interface
nav_order: 4
has_children: false
---

# C and RTL Simulation

## Building the Project
Having designed the IP, we can now simulate it.
First, follow the instructions to [build the Vitis project](../../support/amd/vitis_build.md) but use the design and testbench files in:

* [Launch Vitis HLS](./lauching.md)
* Go to **File → New Component → HLS**.  You will set a sequence of items:
   * For **Component name** select `hls_component`
   * For **Component location** select `hwdesign/fifoif/fifo_fun_vitis`
   * For **Configuration File** select `Empty File`
   * For **Source Files** set:
       * Top Function: `simp_fun`
       * Design Files: Add `src/fifofun.cpp`
       * Testbench: Add `src/tb_fifofun.cpp`
   * For **Hardware** part select the [part number](../../support/amd/fpga_part.md)
   * For **Settings** keep as default, with the clock frequency to `100MHz`
* Vitis will reopen with the project.

## Simulation 
In the Flow panel (left):

* Run the **C Simulation->Run**.
    * You should get that the five tests pass
* Run **C synthesis**
    * This step will synthesize the IP from the Vitis HLS
* Find the **C/RTL Co-Simulation** section
    * Select the settings (gear box) in the C/RTL Simulation
    * Select `cosim.trace.all` to `all`.  This setting will trace all the outputs.
    * Select the **Run** option to run the simulation 

## Viewing the Command-Response Timing

Now go to the [jupyter notebook](https://github.com/sdrangan/hwdesign/tree/main/fifoif/python/view_axi_stream.ipynb) to view the command-response timing.

