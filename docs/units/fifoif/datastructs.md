---
title: Data structures
parent: Command-Response FIFO Interface
nav_order: 2
has_children: false
---

# Data Structures
To better organize the code, is useful to represent both the command and response via **data structures**,
specifically C++ classes.
The data structure for the command is in the file
`fifo_fun_vitis/src/cmd.h` which contains the data structure:
~~~C
class Cmd {
public:

    ap_int<16> trans_id; // Transaction ID
    ap_int<32> a; // Operand A
    ap_int<32> b; // Operand B
    ...
};
~~~
The structure has the two operands `a` and `b` along with a **transaction ID** `trans_id`.  
Each job is given a transaction ID which is echoed back in the response.  In this way,
missing or out-of-order responses can be tracked.

Similarly, the **response** is given in the file 
`fifo_fun_vitis/src/cmd.h` which contains the data structure:
~~~C
class Resp {
public:

    enum ErrCode : unsigned int {
        NO_ERR = 0,
        SYNC_ERR = 1
    };

    ap_int<16> trans_id; // Transaction ID
    ap_int<32> c; // Operand C
    ap_int<32> d; // Operand D
    ap_uint<8> err_code; // Error Code
    ...
};
~~~
Here, `c` and `d` are the outputs, `trans_id` is the echo of the ID from the command,
and `err_code` is an error code that indicates if there was some problem processing the command.

In addition to the fields in the data structure, there are a large number of functions
for processing the structure, particularly packing and unpacking the data from streams.

## Code auto-generation 

Transfer of data structures over streaming interfaces typically requires **packing**
and **unpacking** of different fields in the structure into discrete words.
The words many be 32 or 64 bits depending on the interface.
Often designers hand write the packing and unpacking routines for the individual structures.
This is too cumbersome.  So, I have created a way that you can automatically generate 
the code.

In `fifo_fun_vitis\python\datastructs.py`, there is a Python description of the command data structure.  For example, the command structure is described by a list of fields:
~~~python
# Command structure
cmd_fields = [
    FieldInfo("trans_id", IntType(16), descr="Transaction ID"),
    FieldInfo("a", IntType(32), descr="Operand A"),
    FieldInfo("b", IntType(32), descr="Operand B")]
~~~
The response structure has a similar description.  
We can then auto-generate the Vitis include files, `cmd.h` and `result.h`
from these descriptions:

* Activate the virtual environment with `xilinxutils`.  See the [instructions](../../support/repo/repo.md)
* Navigate to the directory with the command and response field descriptions: 
~~~bash
    hwdesign/fifoif/fifo_fun_vitis/python
~~~
* Run the command:
~~~bash
    python gen_vitis_code.py
~~~
This program will create `cmd.h` and `result.h` in the directory:
~~~bash
    wdesign/fifoif/fifo_fun_vitis/src
~~~


---

Go to [AXI4-Stream interface](./axistream.md).