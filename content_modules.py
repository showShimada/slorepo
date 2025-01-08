import streamlit as st
import pandas as pd
import modules

def create_one_day_data(main_url):
    st.write("スクレイピングを開始します...")

    try:
        # Get links from the main page
        links = modules.get_links_from_main_page(main_url)
        st.write(f"複数設置機種のリンクを取得しました: {len(links)}件")

        # Initialize an empty DataFrame
        combined_df = pd.DataFrame()

        # Scrape each detail page
        for i, link in enumerate(links):
#            st.write(f"ページ {i + 1}: {link} をスクレイピング中...")
            df = modules.scrape_detail_page(link)
            combined_df = pd.concat([combined_df, df])

        # Get links from the main page
        links = modules.get_links_from_main_page_variety(main_url)
        st.write(f"少数設置機種のリンクを取得しました: {len(links)}件")

        # Scrape each detail page
        for i, link in enumerate(links):
#            st.write(f"ページ {i + 1}: {link} をスクレイピング中...")
            df = modules.scrape_detail_page_variety(link)
            combined_df = pd.concat([combined_df, df])

        summary_by_machine_df = modules.summary_by_machine(combined_df)
        summary_all = modules.summary_by_date(combined_df)

        # Add aggregated info
        combined_df = modules.summary_data_frame(combined_df)

        # Display the result
        st.write("スクレイピングが完了しました。結果を表示します。")
        st.header("日付単位集計データ")
        st.dataframe(summary_all)

        st.header("機種別集計データ")
        st.dataframe(summary_by_machine_df)

        st.header("台別データ")
        st.dataframe(combined_df)

        # Option to download as CSV
        csv = combined_df.to_csv(index=False).encode('utf-8')
        st.download_button("CSVをダウンロード", data=csv, file_name="scraped_data.csv", mime="text/csv")

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")

def get_date_to_choose(target_from,target_to):
    date_to_choose = pd.date_range(start=target_from,end=target_to,freq='D')
    return date_to_choose