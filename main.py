import streamlit as st

def main():
    st.title("データ集計アプリ")
    st.write("単日データ：日付を指定して全台のデータを見れるよ")
    st.write("縦の比較：指定した日付別のデータを機種別、台番別に見れるよ")
    st.write("集計：指定した日付別のデータを集計しできるよ")
    st.write("結果確認：指定した日付の結果と比較対象の日付の集計値がみれるよ")

if __name__ == "__main__":
    main()
