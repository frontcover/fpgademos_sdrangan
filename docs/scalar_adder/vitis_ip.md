---
title: Creating the Vitis IP
parent: Getting started
nav_order: 1
has_children: false
---

# Creating the Vitis IP
We first create a Vitis HLS project, design and build the Vitis IP for our scalar adder,
and export the IP so that we can use it in Vivado.

## Getting the FPGA Part Number

Before starting the Vitis IP, you will need to follow 
the [instructions for building a Vivado project](../sw_installation/vivado_build.md) with a processor system.
Then, get the FPGA part number for that processing system.

## Creating the Vitis HLS Project

* [Launch Vitis](../sw_installation/installation.md)
* Select **Open Workspace**.  Go to the directory `hwdesign\scalar_adder`.  This is where we will put the workspace.  `Vitis_HLS` will reopen.
* Select **Create component->Create empty HLS component**.  You will walk through the following six steps:
    * For **Name and location**, select component name as `scalar_add` and the location as `hwdesign\scalar_adder\scalar_add_vitis`
    * Set the **Configuration file** select **Empty File** which is the default
    * In **Source Files**, select top function to `add`
    * In the **Hardware** tab, you will need to select the hardware you are targetting.  Select **Part** and search for the FGPA part number from above.
    * In the **Settings** tab, I kept all defaults, except I set the clock speed to either `250MHz` or `300MHz`.
* Now you should have an empty project.
* Sometimes the part number was not correct.  To verify the selection of the part, on the **Flow** panel (left sidebar), go to the `C Synthesis` section and select the settings (gear box).
    * In the `General` tab, there is `part` number.  Set the part number to `xczu48dr-ffvg1517-2-e` or whatever the correct part number is.

## Creating the Vitis IP and Testbench Source files
* In the directory `scalar_add_vitis/src/`,  there is the main source C file, `scalar_add.cpp` describing the functionality for our "IP":
~~~c
    void add(int a, int b, int& c) {
        #pragma HLS INTERFACE s_axilite port=a
        #pragma HLS INTERFACE s_axilite port=b
        #pragma HLS INTERFACE s_axilite port=c
        #pragma HLS INTERFACE s_axilite port=return
        c = a + b;
        }
~~~
This file is already in the git repo, so you do not need to write it.
   * Recall, that in the settings, we stated that `add` is the **top** function.  This function is refering to the function `add` in this file.  It will define the inputs and outputs that we will see in the processing system.
* In the SCALAR_ADD_VITIS explorer pane (left sidebar), right click **Sources** and select **Add Source File** and open `scalar_add.cpp`.   We have now added the file to our project.
Alternatively, you could have selected **New Source File** and created the file here.
* Next create a testbench. Generally, we place the testbenches in a separate directory, which in our case will be: `scalar_add_vitis/testbench`.   Th filee must follow the same name as the component with `tb_` as a prefix.  So, for this case the file will be  `tb_scalar_add.cpp` and located in the `scalar_add_vitis/testbench` directory:
~~~c
    #include <iostream>
    void add(int a, int b, int& c);

    int main() {
      int result;
      add(7, 5, result);
      std::cout << "Result: " << result << std::endl;
      return 0;
    }
~~~

## Synthesizing and Building the Vitis IP

* In the **FLOW** panel (left sidebar), select **C Simulation → Run**.  It should run with a result of 12. This step simulates your C code to verify functional correctness before synthesis.
* Still in the **FLOW** panel, select **C Synthesis → Run**.  
  This step converts your C/C++ function into synthesizable RTL (Verilog/VHDL), targeting the specified FPGA part.
* Next in the **FLOW** panel, select **Package → Run**.  
  This wraps the synthesized RTL into a reusable IP block, complete with metadata and interface definitions.
* The packaging will have created a directory of files containing the *IP* for the adder.  It will be located in 
~~~bash
  scalar_adder_vitis/scalar_add/add/hls/impl/ip
~~~
* Note that we do not need to run the **Implementation** step — this is for creating standalone bitstreams, not ones that will be integrated into a larger FPGA project.

---
Go to [Adding the Vitis IP](./add_ip.md)