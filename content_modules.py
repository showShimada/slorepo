import streamlit as st
import pandas as pd
import modules

def create_one_day_data(main_url):
    # st.write("スクレイピングを開始します...")

    try:
        combined_df = modules.scrape_one_day(main_url)

        summary_by_machine_df = modules.summary_by_machine(combined_df)
        summary_all = modules.summary_by_date(combined_df)

        # Add aggregated info
        combined_df = modules.summary_data_frame(combined_df)

        # Display the result
        st.write("スクレイピングが完了しました。結果を表示します。")
        summary_all = summary_all.set_index('日付')
        st.header("日付単位集計データ")
        st.dataframe(summary_all)

        summary_by_machine_df = summary_by_machine_df.set_index('機種')
        st.header("機種別集計データ")
        st.dataframe(summary_by_machine_df)

        combined_df = combined_df.set_index('台番')
        st.header("台別データ")
        st.dataframe(combined_df)

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")

def get_date_to_choose(target_from,target_to):
    date_to_choose = pd.date_range(start=target_from,end=target_to,freq='D')
    return date_to_choose

def create_vertical_data(main_url,target_dates):
    # st.write("スクレイピングを開始します...")

    try:
        # Initialize an empty DataFrame
        combined_df = pd.DataFrame()

        for target_date in target_dates:
            target_url = main_url + format(target_date,"%Y%m%d") + "/"
            combined_df = pd.concat([combined_df,modules.scrape_one_day(target_url)])

        summary_all = modules.summary_by_date(combined_df)
        summary_by_machine_df = modules.get_pivoted_by_machine(combined_df)
        pivoted_by_machine_no = modules.get_pivoted_by_machine_no(combined_df)

        # Add aggregated info
        combined_df = modules.summary_data_frame(combined_df)

        # Display the result
        st.write("スクレイピングが完了しました。結果を表示します。")
        summary_all = summary_all.set_index('日付')
        st.header("日付単位集計データ")
        st.dataframe(summary_all)

        st.header("機種別集計データ")
        st.dataframe(summary_by_machine_df)

        st.header("台番別データ")
        st.dataframe(pivoted_by_machine_no)

        combined_df = combined_df.set_index('台番')
        st.header("元データ")
        st.dataframe(combined_df)

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")

def create_aggregated_data(main_url,target_dates):
    # st.write("スクレイピングを開始します...")

    try:
        # Initialize an empty DataFrame
        combined_df = pd.DataFrame()

        for target_date in target_dates:
            target_url = main_url + format(target_date,"%Y%m%d") + "/"
            combined_df = pd.concat([combined_df,modules.scrape_one_day(target_url)])

        summary_all = modules.summary_by_date(combined_df)
        summary_by_machine_df = modules.summary_by_machine(combined_df)
        summary_by_machine_no_df = modules.summary_by_machine_no(combined_df)

        # Add aggregated info
        combined_df = modules.summary_data_frame(combined_df)

        # Display the result
        st.write("スクレイピングが完了しました。結果を表示します。")

        summary_all = summary_all.set_index('日付')
        st.header("日付単位集計データ")
        st.dataframe(summary_all)

        summary_by_machine_df = summary_by_machine_df.set_index('機種')
        st.header("機種別集計データ")
        st.dataframe(summary_by_machine_df)

        summary_by_machine_no_df = summary_by_machine_no_df.set_index('台番')
        st.header("台番別データ")
        st.dataframe(summary_by_machine_no_df)

        combined_df = combined_df.set_index('台番')
        st.header("元データ")
        st.dataframe(combined_df)

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")

def create_check_result(main_url,target_dates,target):
    # st.write("スクレイピングを開始します...")

    try:
        # Initialize an empty DataFrame
        combined_df = pd.DataFrame()

        for target_date in target_dates:
            target_url = main_url + format(target_date,"%Y%m%d") + "/"
            combined_df = pd.concat([combined_df,modules.scrape_one_day(target_url)])

        summary_by_machine_df = modules.summary_by_machine(combined_df)
        summary_by_machine_no_df = modules.summary_by_machine_no(combined_df)

        # 確認対象の日のデータ取得
        target_url = main_url + format(target,"%Y%m%d") + "/"
        target_df = modules.scrape_one_day(target_url)

        summary_by_machine_df2 = modules.summary_by_machine(target_df)
        summary_by_machine_no_df2 = modules.summary_by_machine_no(target_df)

        # 確認対象の日のデータと比較対象のデータをコンカチ
        combined_df = pd.concat([combined_df,target_df])
        summary_all = modules.summary_by_date(combined_df)

        # Add aggregated info
        combined_df = modules.summary_data_frame(combined_df)
        summary_by_machine_df2 = summary_by_machine_df2.merge(summary_by_machine_df,on=["機種"])
        summary_by_machine_no_df2 = summary_by_machine_no_df2.merge(summary_by_machine_no_df,on=["台番"])

        # 機種別データフレームの整形
        column_name = ["機種", "勝ち_結果", "台数_結果", "平均差枚_結果", "平均G数_結果", "BB確率_結果", "RB確率_結果", "合成確率_結果", "payout_結果", "合計差枚_結果", "合計G数_結果", "合計BB_結果", "合計RB_結果", "平均BB_結果", "平均RB_結果",
                        "勝ち_比較", "台数_比較", "平均差枚_比較", "平均G数_比較", "BB確率_比較", "RB確率_比較", "合成確率_比較", "payout_比較", "合計差枚_比較", "合計G数_比較", "合計BB_比較", "合計RB_比較", "平均BB_比較", "平均RB_比較"]
        summary_by_machine_df2.columns = column_name

        column_order = ["機種", "勝ち_結果", "台数_結果", "平均差枚_結果", "平均G数_結果", "BB確率_結果", "RB確率_結果", "合成確率_結果", "payout_結果",
                        "勝ち_比較", "台数_比較", "平均差枚_比較", "平均G数_比較", "合計差枚_比較", "合計G数_比較", "BB確率_比較", "RB確率_比較", "合成確率_比較", "payout_比較"]
        summary_by_machine_df2 = summary_by_machine_df2[column_order]

        # 台番別データフレームの整形
        column_name = ["台番", "勝ち_結果", "台数_結果", "差枚_結果", "G数_結果", "BB確率_結果", "RB確率_結果", "合成確率_結果", "payout_結果", "合計差枚_結果", "合計G数_結果", "合計BB_結果", "合計RB_結果", "平均BB_結果", "平均RB_結果",
                        "勝ち_比較", "台数_比較", "平均差枚_比較", "平均G数_比較", "BB確率_比較", "RB確率_比較", "合成確率_比較", "payout_比較", "合計差枚_比較", "合計G数_比較", "合計BB_比較", "合計RB_比較", "平均BB_比較", "平均RB_比較"]
        summary_by_machine_no_df2.columns = column_name

        column_order = ["台番", "差枚_結果", "G数_結果", "BB確率_結果", "RB確率_結果", "合成確率_結果", "payout_結果",
                        "勝ち_比較", "台数_比較", "平均差枚_比較", "平均G数_比較", "合計差枚_比較", "合計G数_比較", "BB確率_比較", "RB確率_比較", "合成確率_比較", "payout_比較"]
        summary_by_machine_no_df2 = summary_by_machine_no_df2[column_order]


        # Display the result
        st.write("スクレイピングが完了しました。結果を表示します。")

        summary_all = summary_all.set_index('日付')
        st.header("日付単位集計データ")
        st.dataframe(summary_all)

        summary_by_machine_df2 = summary_by_machine_df2.set_index('機種')
        st.header("機種別集計データ")
        st.dataframe(summary_by_machine_df2)

        summary_by_machine_no_df2 = summary_by_machine_no_df2.set_index('台番')
        st.header("台番別データ")
        st.dataframe(summary_by_machine_no_df2)

        combined_df = combined_df.set_index('台番')
        st.header("元データ")
        st.dataframe(combined_df)

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")