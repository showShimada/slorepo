import streamlit as st
from urllib.parse import quote, urljoin
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import modules
import content_modules

def main():
    st.title("縦の比較")

    # Main URL
    dict_url = modules.get_dict_url()
    selected_hole = st.selectbox('店舗を選択',dict_url)
    main_url =  dict_url[selected_hole]

    target_from = st.date_input('開始の日付を選択')
    target_to = st.date_input('終了の日付を選択')

    date_to_choose = content_modules.get_date_to_choose(target_from,target_to)
    target_dates = st.multiselect("集計対象の日付を選択",date_to_choose)
    
    if st.button('実行'):
        content_modules.create_vertical_data(main_url,target_dates,selected_hole)

if __name__ == "__main__":
    main()