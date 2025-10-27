// Vector multiplication function
#include "../include/poly_vec.h"
#include <string.h>

void poly_vec(
    float *x_in,         // AXI master input
    float *y_out,        // AXI master output
    float coeffs[POLY_DEGREE+1],     // AXI-lite control: coeffs[0]=a, coeffs[1]=b, coeffs[2]=c, coeffs[3]=d
    int size             // AXI-lite control
) {
#pragma HLS INTERFACE m_axi port=x_in  offset=slave bundle=gmem
#pragma HLS INTERFACE m_axi port=y_out offset=slave bundle=gmem
#pragma HLS INTERFACE s_axilite port=coeffs bundle=control
#pragma HLS INTERFACE s_axilite port=size   bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

    float x_buf[MAX_SIZE];
    float y_buf[MAX_SIZE];

#pragma HLS ARRAY_PARTITION variable=x_buf type=cyclic factor=UNROLL_FACTOR  dim=1
#pragma HLS ARRAY_PARTITION variable=y_buf type=cyclic factor=UNROLL_FACTOR  dim=1

    // Load input vector
    load_loop: for (int i = 0; i < size; i++) {
    #pragma HLS PIPELINE II=1
        x_buf[i] = x_in[i];
    }

    // Load the coefficients
    float a0 = coeffs[0];
    float a1 = coeffs[1];
    float a2 = coeffs[2];
    float a3 = coeffs[3];

    // Compute polynomial
    compute_loop: for (int i = 0; i < size; i++) {

    #if UNROLL_FACTOR > 1
    #pragma HLS unroll factor=UNROLL_FACTOR
    #elif PIPELINE_EN
    #pragma HLS pipeline II=1
    #else
    #pragma HLS pipeline off 
    #endif
        float x0 = x_buf[i];
        float x1 = x0 * x0;
        float x2 = x1 * x0;
        float xi = x_buf[i];
        y_buf[i] = a3*x2 + a2*x1 + a1*xi + a0;
    }

    // Store result
    store_loop: for (int i = 0; i < size; i++) {
    #pragma HLS PIPELINE II=1
        y_out[i] = y_buf[i];
    }
}
