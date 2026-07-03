import numpy as np
import pandas as pd


def main():
    value = [[7, 5], [5, 1], [3, -1]]
    df = pd.DataFrame(value)

    value2 = [[1, -3]]
    df2 = pd.DataFrame((value2))

    print(df.add(df2))  # return 에만 변화를 줌
    print(df.sub(df2))
    print(df.mul(df2))
    print(df.div(df2))
    print(df + df2)
    print(df - df2)
    print(df * df2)
    print(df / df2)

    print(df.add(df2, fill_value=0))
    print(df.sub(df2, fill_value=0))
    print(df.mul(df2, fill_value=1))
    print(df.div(df2, fill_value=1))

    print(df.sum(0))
    print(df.mean(0))
    print(df.std(0))
    print(df.var(0))

    print(df.sum(1))
    print(df.mean(1))
    print(df.std(1))
    print(df.var(1))


if __name__ == "__main__":
    main()
