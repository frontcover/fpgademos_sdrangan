---
title: AXI4-Stream protocol
parent: Command-Response FIFO Interface
nav_order: 3
has_children: false
---

# AXI4-Stream Protocol Overview

## Protocol Structure

We send the command and responses via the **AXI4-Stream protocol**, a
lightweight data transfer mechanism that uses a simple **handshake** between the source (master) and sink (slave). Data is sent in units called **bursts**, which are sequences of one or more data **beats**. Each beat is transferred when both sides agree: the source asserts **TVALID** to indicate valid data, and the sink asserts **TREADY** to signal readiness to accept it.

Within a burst:

- **TVALID** stays high while the source has data to send.
- **TREADY** may toggle depending on whether the sink can accept data.
- A **transfer** occurs only when both TVALID and TREADY are high in the same cycle.

This handshake ensures **flow control**: the source never overruns the sink, and the sink can apply backpressure by deasserting TREADY.

---

## Handshake States

| TVALID | TREADY | State          | Description                          |
|--------|--------|----------------|--------------------------------------|
| 1      | 1      | **Transfer**   | Data beat accepted (handshake occurs)|
| 1      | 0      | **Sink stall** | Source has data, sink not ready      |
| 0      | 1      | **Source idle**| Sink ready, source has no data       |
| 0      | 0      | **Quiescent**  | Both inactive, no transfer possible  |


---

At the end of a burst, the source asserts **TLAST** to mark the final beat, signaling the sink that the burst is complete.

## Implementing the Interfaces in the IP

The basic structure for the Vitis IP is as follows:
The function has two AXI-Stream interfaces, `cmd_stream` and `result_stream`.
There is an inifite loop that waits for each command packet, processes it,
and sends a response to the output stream.

~~~C

void simp_fun(
    hls::stream<stream_t>& cmd_stream,
    hls::stream<stream_t>& result_stream,
    ... // other AXI-Lite registers
) {
#pragma HLS INTERFACE axis port=cmd_stream
#pragma HLS INTERFACE axis port=result_stream
#pragma HLS INTERFACE ap_ctrl_chain port=return

    while (!cmd_stream.empty()) {
        Cmd cmd;

        // Read command from input FIFO using stream_read
        bool tlast_ok = cmd.stream_read<stream_t>(cmd_stream);

        // Proccess cmd and compute res
        // res = ...
        

        // Write result to output FIFO using stream_write
        res.stream_write<stream_t>(result_stream, true); // Assert TLAST on final word
    }
}
~~~

The functions `stream_read` and `stream_write` are methods of the `Cmd` and `Result`
classes.  The functions unpack and pack the data fields from the words in the structure.
