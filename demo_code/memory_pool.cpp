// memory_pool.cpp - Memory pool buffer management simulation
// This file is used for testing deterministic static analysis rules.

#include <iostream>
#include <cstring>

class MemoryPool {
private:
    char* raw_buffer;
    size_t pool_size;

public:
    MemoryPool(size_t size) {
        pool_size = size;
        // Contains Memory Leak Risk (Raw New)
        raw_buffer = new char[size]; 
    }

    ~MemoryPool() {
        // Warning: raw_buffer might not be deleted if destructor is not clean
        // or if exceptions occur, but raw new itself is the primary scan target
    }

    void copy_tag(const char* tag) {
        // Contains Unsafe Buffer Copy (strcpy)
        std::strcpy(raw_buffer, tag);
    }

    void process_matrices(int** A, int** B, int** C, int rows, int cols) {
        // Contains O(N^2) Nested Loop
        for (int i = 0; i < rows; ++i) {
            for (int j = 0; j < cols; ++j) {
                C[i][j] = A[i][j] * B[i][j];
            }
        }
    }
};

int main() {
    MemoryPool pool(1024);
    pool.copy_tag("INITIAL_TAG");
    return 0;
}
