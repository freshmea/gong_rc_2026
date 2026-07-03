# pip install matplotlib
import matplotlib.pyplot as plt
import numpy as np


def main():
    data = np.random.random(10)
    plt.plot(data)
    plt.show()
    data = np.random.random(30).reshape(10, 3)
    plt.plot(data)
    plt.show()


if __name__ == "__main__":
    main()
