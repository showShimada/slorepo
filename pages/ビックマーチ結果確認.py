import streamlit as st
from urllib.parse import quote, urljoin
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import content_modules

def main():
    st.title("ビックマーチ結果確認")

    # Main URL
    main_url = "https://www.slorepo.com/hole/e38393e38383e382afe3839ee383bce38381e69db1e7bf92e5bf97e9878ee5ba97code/"

    target = st.date_input('確認したい対象の日付を選択')

    target_from = st.date_input('開始の日付を選択')
    target_to = st.date_input('終了の日付を選択')

    date_to_choose = content_modules.get_date_to_choose(target_from,target_to)
    target_dates = st.multiselect("集計対象の日付を選択",date_to_choose)
    
    if st.button('実行'):
        content_modules.create_check_result(main_url,target_dates,target)

if __name__ == "__main__":
    main()