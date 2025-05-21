import pandas as pd
import opendal
from dotenv import load_dotenv
import os


def main():
    load_dotenv(verbose=True)
    # Init an operator.
    # for fs operator
    target_vars = [
        'OPENDAL_S3_ENDPOINT', 'OPENDAL_S3_REGION', 'OPENDAL_S3_BUCKET',
        "OPENDAL_S3_ACCESS_KEY_ID", "OPENDAL_S3_SECRET_ACCESS_KEY",
        "OPENDAL_S3_ENABLE_VIRTUAL_HOST_STYLE", "OPENDAL_S3_ROOT"
    ]
    env_vars = {
        var: os.environ.get(var, None)
        for var in target_vars
    }
    print(env_vars)

    op = opendal.Operator("s3",
                          root=env_vars.get("OPENDAL_S3_ROOT"),
                          bucket=env_vars.get("OPENDAL_S3_BUCKET"),
                          region=env_vars.get("OPENDAL_S3_REGION"),
                          enable_virtual_host_style="true" if env_vars.get(
                              "OPENDAL_S3_ENABLE_VIRTUAL_HOST_STYLE") == "on" else "false",
                          access_key_id=env_vars.get("OPENDAL_S3_ACCESS_KEY_ID"),
                          secret_access_key=env_vars.get("OPENDAL_S3_SECRET_ACCESS_KEY"),
                          )

    # Create and write a csv file
    op.write("test.csv", b"name,age\nAlice,25\nBob,30\nCharlie,35")

    # Open and read the DataFrame from the file.
    with op.open("test.csv", mode="rb") as file:
        read_df = pd.read_csv(file)
        print(f"read_df: {read_df}")


if __name__ == "__main__":
    main()
