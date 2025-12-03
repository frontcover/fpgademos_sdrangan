---
title: Creating the Vitis IP
parent: Simple Scalar Accelerator
nav_order: 1
has_children: false
---

# Creating the Vitis IP


## High Level Synthesis (HLS)

We first design our Vitis IP to be incorporated into the FPGA.
We will design the IP with so‑called **High Level Synthesis (HLS)**, which means we describe the behavior of our design using a high‑level programming language such as C or C++, rather than writing out the detailed hardware connections ourselves. 

The synthesis tool then automatically translates this description **Register Transfer Language (RTL)** like Verilog or VHDL.  The RTL describes the 
the exact flow of signals between registers and logic gates.  Prior engineering
desing flows (still used by most companies) is to directly code the RTL.  RTL gives very fine‑grained control but is vastly more time‑consuming and harder for beginners, while HLS allows us to think in terms of algorithms and let the tool handle the low‑level hardware details.


## Creating the Vitis HLS Project

Following the instructions in the [software set-up](../../setup/sw_installation/vitis_build.md) for building a Vitis project:

* [Launch Vitis](../../setup/sw_installation/)
* Select **Open Workspace**.  Go to the directory `hwdesign\scalar_fun`.  This is where we will put the workspace.  `Vitis_HLS` will reopen.
* Select **Create component->Create empty HLS component**.  You will walk through the following six steps:
    * For **Name and location**, select component name as `hls_component` and the location as `hwdesign\scalar_fun\scalar_fun_vitis`
    * Set the **Configuration file** select **Empty File** which is the default
    * In **Source Files**, select top function to `simp_fun`
    * In the **Hardware** tab, you will need to select the hardware you are targetting.  Follow the instructions for [building the Vivado project](../sw_installation/vivado_build.md) to get the part number.  Select **Part** and search for the FGPA part number from above.
    * In the **Settings** tab, I kept all defaults, except I set the clock speed to either `250MHz` or `300MHz`.
* Now you should have an empty project.
* Sometimes the part number was not correct.  To verify the selection of the part, on the **Flow** panel (left sidebar), go to the `C Synthesis` section and select the settings (gear box).
    * In the `General` tab, there is `part` number.  Set the part number to `xczu48dr-ffvg1517-2-e` or whatever the correct part number is.

## Creating the Vitis IP Source File
* In the directory `scalar_fun_vitis/src/`,  there is the main source C file, `scalar_fun.cpp` describing the functionality for our "IP":
~~~c
    void simp_fun(int a, int b, int& c) {
        #pragma HLS INTERFACE s_axilite port=a
        #pragma HLS INTERFACE s_axilite port=b
        #pragma HLS INTERFACE s_axilite port=c
        #pragma HLS INTERFACE s_axilite port=return
        c = a * b;
        }
~~~

The function just multiplies two numbers.  You can change this as you like.
This file is already in the git repo, so you do not need to write it.
   * Recall, that in the settings, we stated that `simp_fun` is the **top** function.  This function is referring to the function `simp_fun` in this file.  It will define the inputs and outputs that we will see in the processing system.
* In the SCALAR_FUN_VITIS explorer pane (left sidebar), right click **Sources** and select **Add Source File** and open `scalar_fun.cpp`.   We have now added the file to our project.
Alternatively, you could have selected **New Source File** and created the file here.

## Creating the Testbench
A **testbench** is a program that tests the IP, generally by giving it inputs and verifying the outputs
match the expected results.
* Generally, we place the testbenches in a separate directory, which in our case will be: `scalar_fun_vitis/testbench`.   The file must follow the same name as the component with `tb_` as a prefix.  So, for this case the file will be  `tb_scalar_fun.cpp` and located in the `scalar_fun_vitis/testbench` directory
* The `tb_scalar_fun.cpp` in the github repo has the following code:
~~~c
    int main() {
      int c;
      int a = 7;
      int b = 5;
      int c_exp = a*b;
      simp_fun(a, b, c);
      std::cout << "Result: " << c << std::endl;

      if (c == c_exp)
          std::cout << "Test passed!" << std::endl;
      else
          std::cout << "Test failed!" << std::endl;
          
      return 0;
  }
~~~
So, it basically gives the IP two numbers and tests the result matches.
Later, we will create more elaborate tests.



---
Go to [Simulate and synthesize the IP](./csynth.md)