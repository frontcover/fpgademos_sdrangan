---
title: Overview
parent: Command-Response FIFO Interface
nav_order: 1
has_children: false
---
# Command and Response Interface Overview

## Problems with Control Register Interfaces

In the [scalar function example](../scalar_fun/), the inputs and outputs were written and read via AXI-Lite control registers via a simple execution model:

* PS sets control registers on the IP
* PS sets a specific register (`ap_start`) to start execution
* PS polls a different register to wait for completion
* PS reads the results from other control registers

This interface is simple to understand and implement, but very inefficient.
The IP cannot do anything while the PS prepares the data and reads and writes the registers.  Hence, the IP often goes under-utilized.  The lack of utilization can be particularly high when the PS is occupied with other tasks as is common in more complex designs.  In this case, there can be a long unused period where the IP is waiting for the next input.
In addition, the PS must continuously poll the IP waiting for the response,
which makes the PS highly inefficient as well.


## Command-Response Interface Overview

The **command-response interface** provides a more efficient method for interaction with the IP that enables
higher utilization on both the IP and PS. In our simple example, the interface works as follows:

* The PS sends the IP a sequence of **commands**.  In our case, each command will contain the inputs `a` and `b`.
* The commands are stored in a **FIFO** meaning they are ready to be consumed by the IP as soon as it is ready.  Hence, there is no delay waiting for the IP since the IP can pre-load the FIFO.
* The IP processes each command in turn, producing a corresponding **response** that contains the outputs `c` and `d`.
* The responses are also stored in a **FIFO**, allowing the PS to read them at its convenience without blocking the IP.
* This decoupling means the PS can issue many commands in advance, and the IP can continuously operate on them without idle cycles, while the PS later collects the results when it is ready.

In summary, the command-response interface eliminates the need for constant polling and ensures that both sides remain busy: the PS can queue work ahead of time, and the IP can process commands back-to-back, leading to much higher throughput and utilization.


## Scalar Function Example
To illustrate how to build and analyze the command-response interface,
we have develop a very simple example in the directory:
~~~bash
    hwdesign/fifoif/fifo_fun_vitis
~~~ 
Similar to the scalar function example, we consider again implementing
a simple function of two variables.  Specifically, in this unit, we will consider the simple scalar function:
~~~C
    int c = a*b; 
    int d = a+b; 
~~~
which takes two inputs `a` and `b` and two outputs `c` and `d`.  Obviously, again, this function is too simple to implement in a custom hardware accelerator.  The point is to illustrate general principles for the command-response interface.


---

Go to [defining command-response data structures](./datastructs.md).