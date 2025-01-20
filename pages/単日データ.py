import streamlit as st
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import modules
import content_modules

def main():
    st.title("単日データ作成")

    dict_url = modules.get_dict_url()
    selected_hole = st.selectbox('店舗を選択',dict_url)
    target_date = format(st.date_input('確認したい対象の日付を選択'),"%Y%m%d")

    # Main URL
    main_url =  dict_url[selected_hole] + target_date + "/"

    if st.button('実行'):
        content_modules.create_one_day_data(main_url,selected_hole)

if __name__ == "__main__":
    main()
