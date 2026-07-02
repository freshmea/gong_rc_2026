from pathlib import Path

# pip install seaborn
import numpy as np
import pandas as pd
import seaborn as sns


def main():
    BASE = Path(__file__).parent
    df = pd.read_csv(BASE / "weather.csv", index_col=0, header=0)
    print(df)
    df = sns.load_dataset("titanic")
    df.to_csv(BASE / "titanic.csv")


if __name__ == "__main__":
    main()
