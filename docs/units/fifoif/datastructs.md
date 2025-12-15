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

In `fifo_fun_vitis\datastructs.py`, there is a Python description of the command data structure.  Then, a class `DataStructGen` is called to auto-generate the `cmd.h` file.
Similar code is available for `resp.h`.  
This auto-generation will save a lot of time and reduce errors.  

~~~python
# Command structure
fields = [
    FieldInfo("trans_id", IntType(16), descr="Transaction ID"),
    FieldInfo("a", IntType(32), descr="Operand A"),
    FieldInfo("b", IntType(32), descr="Operand B")]
cmd_struct = DataStructGen("Cmd", fields)
cmd_struct.stream_bus_widths = stream_bus_widths
cmd_struct.gen_include(include_file="cmd.h")
~~~
You can then synthesize the include files `cmd.h` and `result.h` by:
* Activate the virtual environment with `xilinxutils`.  See the [instructions](../../support/repo/repo.md)
* Navigate to the directory with the source code: 
~~~bash
    hwdesign/fifoif/fifo_fun_vitis/src
~~~
* Run the command:
~~~bash
    python datastructs.py
~~~
This program will create `cmd.h` and `result.h`.


---

Go to [AXI4-Stream interface](./axistream.md).