# matrix_ops.py - Matrix Operations Utility
# This file is used for testing deterministic static analysis rules.

active_matrix = None

def compute_matrix_product(matrix_a, matrix_b):
    """
    Computes matrix multiplication using standard loops.
    Contains O(N^3) nested loop algorithmic bottleneck.
    """
    n = len(matrix_a)
    m = len(matrix_a[0])
    p = len(matrix_b[0])
    
    # Initialize result matrix
    result = [[0 for _ in range(p)] for _ in range(n)]
    
    # Nested loops bottleneck
    for i in range(n):
        for j in range(p):
            for k in range(m):
                result[i][j] += matrix_a[i][k] * matrix_b[k][j]
                
    return result

def cache_matrix_state(matrix, cache=[]):
    """
    Caches the matrix state in a mutable default argument.
    Contains Mutable Default Argument architectural smell.
    """
    global active_matrix  # Contains Global Variable Modification smell
    active_matrix = matrix
    
    try:
        cache.append(matrix)
    except Exception:
        pass  # Contains Unsafe Exception Handling (Silent Except)
        
    return len(cache)
