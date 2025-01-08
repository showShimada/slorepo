import streamlit as st
from urllib.parse import quote, urljoin
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import content_modules

def main():
    st.title("カレンダーを選択して日付のリストを作成")

    target_from = st.date_input('開始の日付を選択')
    target_to = st.date_input('終了の日付を選択')

    date_to_choose = content_modules.get_date_to_choose(target_from,target_to)
    target_dates = st.multiselect("choose date to aggregate",date_to_choose)

    for target_date in target_dates:
        st.write(format(target_date,"%Y%m%d"))

if __name__ == "__main__":
    main()