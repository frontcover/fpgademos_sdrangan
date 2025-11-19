---
title: Simulating the RTL
parent: Getting started
nav_order: 2
has_children: false
---

# Simulating the Synthesized Vitis IP

* If Vitis is not already open from the previous step:
    * [Launch Vitis](../sw_installation/installation.md)
    * Open the workspace for the for the Vitis IP that you were using, which should be in `fpgademos/scalar_adder/scalar_add_vitis`
* In the **Flow panel** (left sidebar), select **C/RTL Simulation->Run**
    * This command will execute a RTL-level simulation of the synthesized IP

## Extracting VCD Files

The C/RTL simulation that is run from the Vitis GUI is an `.wbd` (waveform database) format.
This format is an AMD proprietary format and cannot be read by other programs,
although you can see it in the Vivado viewer.  So, we will modify the simulation to export 
an alternative open-source **VCD** or [**Value Change Dump**](https://en.wikipedia.org/wiki/Value_change_dump) format.  VCD files can be read by many programs including python.

I wrote a simple python file that modifies the simulation files to capture the VCD output and re-runs the simulation.
* `cd` to the directory of the Vitis IP project.  In the scalar adder project, this is in `fpgademos\scalar_adder\scalar_adder_vitis`
* Locate the directory for the component to run the simulation.  In this case, it is in the sub-directory: 
~~~bash
    scalar_adder_vitis\scalar_add\add
~~~
* For Windows, run the command
~~~bash
    python ..\..\common\xsim_vcd_win.py scalar_add\add
~~~
Or whatever the sub-directory name is for the component.
* We have not yet created a version of the script for Linux.
* After running the script, there will be a VCD file with the simulation:
~~~bash
    scalar_adder_vitis\vcd\dump.vcd
~~~

## Extracting the VCD Files Manually 

You do not have to do this gory step, but if want to know how the python script above does, you can following these steps:

* After running the initial simulation, locate the directory where the simulation files are.
For the scalar adder simulation, it will be in something like:
~~~bash
    scalar_add_vitis\scalar_add\add\hls\sim\verilog
~~~
This large directory contains automatically generated RTL files for the testbench along with simuation files.
We will modify these files to output a VCD file and re-run the simulation. 
* In this directory, there will be a file `add.tcl` which sets the configuration for the simulation.  Copy the file to a new file `add_vcd.tcl` and modify as follows:
   *  Add initial lines at the top of the file (before the `log_wave -r /`) line
~~~bash
    open_vcd
    log_vcd * 
~~~
    * At the eend of the file there is 
~~~
    run all
    quit
~~~
    Modify these lines to:
~~~
    run all
    close_vcd
    quit
~~~

* In the same directory, there is a file, `run_xsim.bat`.  
   * There should be a line like
~~~bash
    call C:/Xilinx/2025.1/Vivado/bin/xsim  ... -tclbatch add.tcl -view add_dataflow_ana.wcfg -protoinst add.protoinst
~~~
   * Copy just this line to a new file `run_xsim_vcd.bat` and modify that line to:
~~~bash
    cd /d "%~dp0"
    call C:/Xilinx/2025.1/Vivado/bin/xsim  ... -tclbatch add_vcd.tcl -view add_dataflow_ana.wcfg -protoinst add.protoinst
~~~
That is, we add a `cd /d` command to make the file callable from a different directory, and we change the `tclbatch` file from `add.tcl` to `add_vcd.tcl`
* Go back to the directory `scalar_add_vitis` Re-run the simulation with 
~~~powershell
    ./run_xsim_vcd.bat
~~~
This will re-run the simulation and create a `dump.vcd` file of the simulation data.

## Viewing the Timing Diagram
After you have created VCD file, you can see the timing diagram from the [jupyter notebook](https://github.com/sdrangan/fpgademos/tree/main/scalar_adder/notebooks/view_timing.ipynb).

