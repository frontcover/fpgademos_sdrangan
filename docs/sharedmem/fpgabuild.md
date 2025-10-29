---
title: Building the FPGA project
parent: Shared Memory PS Interface
nav_order: 3
has_children: false
---

# Creating the Vivado project

## Creating the project with the MPSOC
We first create an Vivado project with the MPSOC:

* Launch Vivado (see the [installation instructions]({{ site.baseurl }}/docs/installation.md#launching-vivado)):
* Select the menu option `File->Project->New...`.  
   * For the project name, use `vmult_vivado`.  
   * In location, use the directory `fpgademos/vec_mult`.  The Vivado project will then be stored in `fpgademos/vec_mult/vmult_vivado`.
* Select `RTL project`.  
   * Leave `Do not specify sources at this time` checked.
* For `Default part`, select the `Boards` tab and then select `Zynq UltraScale+ RFSoC 4x2 Development Board`.
* The Vivado window should now open with a blank project.

## Add and configure the Zynq Processor
* In the `Block Design` window select the `Add IP (+)` button.  Add the `Zynq UltraScale+ MPSoC`.  This will add the MPSoC to the design.
* Add the Slave AXI on the PS.  Recall that this is the interface that will be used by the IP to access the DDR.
   * Double click the `Zynq UltraScale+ MPSoC` that you just added.
   * On the `Page Navigator` panel (left) select `Switch to Advanced Mode`. 
   * Select`PS-PL connection->Slave Interface->AXI HP0 FPD`.  The `FPD` stands for the *full power domain* which includes the ARM core, DDR controller, and high performance AXI ports.
   * Set the bit width to 32 since we will be using floating points.  
* Run the `Connection automation`
* Connect the `pclk` to the `maxihpm0_fpd_aclk`, `maxihpm1_fpd_aclk`, and `saxihp0_fpd_aclk` ports.  

## Adding the Vitis IP to Vivado
* Go to `Tools->Settings->Project Settings->IP->Repository`.  Select the `+` sign in `IP Repositories`.  Navigate to the directory with the adder component.  In our case, this was at:  `fpgademos/vector_mult/vmult_vitis/vmult_hls/vec_mult/hls/impl/ip`.  
* Select the `Add IP` button (`+`) again.  Add this IP.  Now the `Vec_Mult` block should show up as an option.  If it doesn't it is possible that you synthesized for the wrong FPGA part number.  
* You should see an Vitis IP block with ports `s_axi_control`, `interrupt`, `m_axi_gmem` and some clocks.  Select the `run block automation`.
* Manually connect the `m_axi_gmem` on the Vitis IP to the `S_AXI_HP0_FPD` which connects the master AXI on the IP to the DDR controller on the PS.  
* Connect the `interrupt` on the Vitis IP to the `pl_ps_irq0` so that the PS can see the Vitis IP interrupt.
* Select the `vect_mult` block.  In the `Block Properties` panel, select the `General` tab, and rename the block to `vect_mult`.  This is the name that we will use when calling the function from `PYNQ`.

## Creating the FPGA Bitstream in Vivado
Follow the similar steps in Scalar adder demo 

We are now ready to create the bitstream to program the FPGA with the design.

* Generate output products:
   - In the `Block Design` window, open the `Sources` panel (left).
   - Right-click `design_1.bd` and select `Generate Output Products...`.
   - This step converts the Block Design (BD) into HDL netlists, making it usable for synthesis.
* Create HDL wrapper:
   - The first time you generate output products, you need to generate the BD in a top-level module that Vivado can synthesize.  You only need to do this once.  If you later make chnages, you do not need to re-run this step.
   - Right-click `design_1.bd` again and select `Create HDL Wrapper...`.
   - Choose "Let Vivado manage wrapper and auto-update" (recommended).
* Run Synthesis
   - In the **Flow Navigator** panel (left), click **Run Synthesis**.
   - This converts your HDL design into a *netlist*—a set of logic elements and their interconnections.
   - You’ll see a pinwheel and the message `Running synthesis...` in the top right.
   - For simple designs, this finishes in under a minute. For larger ones, synthesis (and later steps) can take hours—so enjoy the speed while it lasts!
* Run Implementation:
   - Still in the `Flow Navigator`, click `Run Implementation`.
   - This step physically maps the synthesized logic onto the FPGA fabric.
   - Expect a few minutes of processing time.
* Generate Bitstream
   - Finally, click `Generate Bitstream` in the `Flow Navigator`.
   - This creates the `.bit` file that programs the FPGA with your design.


## Creating a PYNQ Overlay

A **PYNQ overlay** is a packaged hardware design (bitstream + metadata) that can be loaded and controlled from Python on a PYNQ-enabled board (like ZCU111, ZCU104 or RFSoC). It abstracts the FPGA logic into a Python-friendly interface.
Follow the following steps to create the PYNQ overlay.

* Locate your bitstream and metadata file.  Vivado can place the files in crazy locations.  So, I suggest you go to the top directory and run the following command from the Vivado project directory for this demo:
~~~bash
    find . -name *.bit
    find . -name *.hwh
~~~
You will locate files with names like:
    *  `scalar_adder_wrapper.bit` — the FPGA configuration file
    * `scalar_adder.hwh` — the hardware handoff file with IP metadata
They are generally in two different directories.  
*  In the same directory as the `.bit` file, find the TCL file, like `scalar_adder_wrapper.tcl`. This file is useful for scripting.  For some reason, there may be multiple `tcl` files in the Vivado project directory.  Take the one in the same directory as the `.bit` file.
* Copy all the files to the `overlay` directory and rename them as:  `scalar_adder.bit`, `scalar_adder.hwh`, `scalar_adder.tcl`.

## Connecting to the RFSoC

* Now follow the instructions on the [RFSoC-PYNQ getting started page](https://www.rfsoc-pynq.io/rfsoc_4x2_getting_started.html).
You should be able to connect to the browser from the host PC at `http://192.168.3.1/lab`. 
* Enter the password `xilinx`.
* Create a directory `scalar_add_demo` with a subdirectory `overlay`.  In the future, I will make this so you can clone the git repo here and have the files on the FPGA board.
* Upload the files in the `overlay` directory to the `overlay` directory on the FPGA board



