
# FPGA Demos

The long-term goal of this repository is to create a series of modular FPGA demos designed to teach hardware/software co-design using Vitis, Vivado, PYNQ, and Python-based simulation.  In going through these demos, you will learn:

* Identify computationally demanding tasks suitable for hardware acceleration.
* Design efficient hardware and software accelerators using state-of-the-art Vitis HLS 
* Simulate and evaluate accelerators with in Vivado and python
* Integrate accelerators in processor-based systems
* Deploy projects onto FPGA boards with PYNQ-based python interfaces

<img src="./docs/images/pynq-z2.png" alt="Pynq-Z2 board" width="400"/>

*Image source: [AMD University Program – PYNQ-Z2 Board](https://www.amd.com/en/corporate/university-program/aup-boards/pynq-z2.html)*

## Pre-Requisites and Target Audience

This course is designed with the idea that *anyone* with a standard background in software can learn hardware with the right methodology.  *Anyone* can tap into the amazing performance that custom hardware can offer.

Hardware acceleration enables dramatically faster computation in myriad areas including machine learning, signal processing, scientific computation, and robotics to name a few.
It is our hope that the material will be of value to students and
engineers for any discipline that hardware can help. 

## Target Platforms and Hardware Required

Right now, the demos will focus on two FPGA platforms:

* [**PYNQ-Z2**](https://www.amd.com/en/corporate/university-program/aup-boards/pynq-z2.html):  A low-cost, easy-to-use board ideal for teaching.  We are considering using this platform as an introductory hardware design class at NYU.
* [**RFSoC 4x2**](https://www.amd.com/en/corporate/university-program/aup-boards/rfsoc4x2.html):  A more powerful, but still relatively low-cost, board for specifically design wireless communications with high-speeds ADCs.

The details for most of the demos are only in one of the two platforms.  However, most of the demos can be adapted either of the boards, or other FPGA boards.  Also, even if you do not have a board,
you will still be able to do the design and simulation of the hardware.

## People

The material is developed by [Sundeep Rangan](https://wireless.engineering.nyu.edu/sundeep-rangan/), a Professor of ECE at New York University and Director of [NYU Wireless](https://wireless.engineering.nyu.edu/).  


## Work in Progress

The site is still under construction and I have just added a few items.  Long-term I am hoping to add a lot more demos as well
as class material like lecture notes and problems.

## Feedback

I would love to get your feedback -- positive or negative.  Feel free to email me, or better yet, send me a Pull Request.
.


## Github pages

Go to the [Github pages](https://sdrangan.github.io/hwdesign) for more.




