import pandas as pd


def main():
    df = pd.read_excel("data.xls", engine="xlrd")
    df["學號"] = df["學號"].astype("string")
    df["姓名"] = df["姓名"].astype("string")
    df["課程碼"] = df["課程碼"].astype("string")
    df["課程名稱"] = df["課程名稱"].astype("string")
    df["成績"] = pd.to_numeric(df["成績"], errors="coerce")
    df["姓名"] = df["姓名"].str.strip()
    df["學號"] = df["學號"].str.strip()
    df["課程碼"] = df["課程碼"].str.strip()
    df["課程名稱"] = df["課程名稱"].str.strip()

    student_info = df[["學號", "姓名"]].drop_duplicates(
        ignore_index=True
    )  # 姓名，學號對照
    student_scores = {
        sid: df[["課程碼", "課程名稱", "成績"]].reset_index(drop=True)
        for sid, df in df.groupby("學號")
    }  # 學號對應的成績



if __name__ == "__main__":
    main()
