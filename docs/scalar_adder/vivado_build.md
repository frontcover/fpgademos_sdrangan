---
title: Creating the Vivado Project
parent: Getting started
nav_order: 1
has_children: false
---

# Creating the Vivado project

We first create an Vivado project with the MPSOC:

* Launch Vivado (see the [installation instructions]({{ site.baseurl }}/docs/installation.md#launching-vivado)):
* Select the menu option `File->Project->New...`.  
   * For the project name, use `scalar_adder_vivado`.  
   * In location, use the directory `fpgademos/scalar_adder`.  The Vivado project will then be stored in `scalar_adder/scalar_adder_vivado`.
* Select `RTL project`.  
   * Leave `Do not specify sources at this time` checked.
* For `Default part`, select the `Boards` tab and then select `Zynq UltraScale+ RFSoC 4x2 Development Board`.
* The Vivado window should now open with a blank project.
* You will see a number of files including the project directory, `scalar_adder\scalar_add_vivado`.
* Before the next step, we need to to find the precise target part number of the FPGA that the IP will run on.  This target part number will be used for Vitis in the next step:
   * Select the menu option `Report->Report IP Status`.  This will open a panel `IP status` at the bottom.
   * In this panel, you can see the part number for something like `/zynq_ultra_ps_e_0`.  That part number will be something like `xczu48dr-ffvg1517-2-e`

---

Go to [Creating the Vitis IP](./vitis_ip.md)