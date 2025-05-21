import pandas as pd

import opendal


def main():
    # Init an operator.
    # for fs operator
    op = opendal.Operator("fs", root="/Users/dingwenjiang/workspace/codereview/pydemos/misc")


    # Create and write a csv file
    op.write("test.csv", b"name,age\nAlice,25\nBob,30\nCharlie,35")

    # Open and read the DataFrame from the file.
    with op.open("test.csv", mode="rb") as file:
        read_df = pd.read_csv(file)
        print(f"read_df: {read_df}")


if __name__ == "__main__":
    main()