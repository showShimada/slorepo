import streamlit as st
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
#import modules
import content_modules

def main():
    st.title("ビックマーチ単日データ作成")

    target_date = st.text_input('日付を指定：YYYYMMDD')

    # Main URL
    main_url = "https://www.slorepo.com/hole/e38393e38383e382afe3839ee383bce38381e69db1e7bf92e5bf97e9878ee5ba97code/" + target_date + "/"

    if st.button('実行'):
        content_modules.create_one_day_data(main_url)

if __name__ == "__main__":
    main()
