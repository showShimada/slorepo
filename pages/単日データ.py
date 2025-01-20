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
    target_date = st.text_input('日付を指定：YYYYMMDD')

    # Main URL
    main_url =  dict_url[selected_hole] + target_date + "/"

    if st.button('実行'):
        content_modules.create_one_day_data(main_url,selected_hole)

if __name__ == "__main__":
    main()
