import numpy as np


def main():
    arr = np.array([1, 2, 3], dtype=np.int8)
    print(type(arr), arr)
    print(arr.ndim, arr.shape, arr.dtype)


if __name__ == "__main__":
    main()
