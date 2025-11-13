

typedef struct {
    float x
    int exp;
} input_t;



void exp( fifo <input_t> &in_fifo, fifo <float> &out_fifo, int n) {

    while (1) {
        input_t in_val = in_fifo.read();

        float x  = in_val.x;
        int exp = in_val.exp;
        float y = 1.0;
        for (int i = 0; i < exp; i++) {
            y =  y * x;
        }

        out_fifo.write(y);
    }
}