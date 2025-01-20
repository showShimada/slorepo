
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import quote, urljoin
import urllib.request, urllib.error
from io import StringIO

def get_links_from_main_page(url):
    """Main page scraper to get all links within a specific table."""
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('figure', class_='wp-block-table2')

    if table is None:
        raise ValueError("指定されたクラス 'wp-block-table2' が見つかりませんでした。")

    # リンクを取得してエンコード
    links = [urljoin(url, a['href']) for a in table.find_all('a', href=True)]
    return links

def get_links_from_main_page_variety(url):
    """Main page scraper to get all links within a specific table."""
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find_all('figure', class_='wp-block-table2')[1]

    if table is None:
        raise ValueError("指定されたクラス 'wp-block-table2' が見つかりませんでした。")

    # リンクを取得してエンコード
    links = [urljoin(url, a['href']) for a in table.find_all('a', href=True)]
    return links

def scrape_detail_page(url):
    """Scrape the detail page for table data and additional information."""
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract table data
    table = soup.find('table', class_='table2')
    df = pd.read_html(StringIO(str(table)))[0]

    # Set index to "台番" and drop "平均" row
    df = df.set_index('台番')
    df = df[df.index != '平均']
    df = df.drop(columns='合成')
    df.reset_index(inplace=True)

    # Extract additional information
    machine = soup.select_one('#post-145 > div > h4 > strong').get_text(strip=True)
    date = soup.select_one('#post-145 > div > h6 > a:nth-child(3)').get_text(strip=True)

    # Add columns for "機種" and "日付"
    df['機種'] = machine
    df['日付'] = date
    df['日付'] = df['日付'].str.replace(r'\([^\)]*\)', '', regex=True)
    df['日付'] = pd.to_datetime(df['日付'], format='%Y/%m/%d')

    return df

def scrape_detail_page_variety(url):
    """Scrape the detail page for table data and additional information."""
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Initialize an empty DataFrame
    combined_df = pd.DataFrame()

    # Extract additional information
    machine = soup.select_one('#post-145 > div > h4 > strong').get_text(strip=True)
    date = soup.select_one('#post-145 > div > h6 > a:nth-child(3)').get_text(strip=True)

    # 'wp-block-columns'クラスを持つdivタグを取得
    columns_divs = soup.find_all('div', class_='wp-block-column')

    for columns_div in columns_divs:
        # Extract machine_no
        machine_no = columns_div.select_one('p').get_text(strip=True)

        # Extract table data
        table = columns_div.find('table')

        df = pd.read_html(StringIO(str(table)))[0]

        # Set index to "台番" and drop "平均" row
        df = df.drop(columns='合成')
        df['台番'] = machine_no

        # Add columns for "機種" and "日付"
        df['機種'] = machine
        df['日付'] = date
        df['日付'] = df['日付'].str.replace(r'\([^\)]*\)', '', regex=True)
        df['日付'] = pd.to_datetime(df['日付'], format='%Y/%m/%d')

        combined_df = pd.concat([combined_df, df])

    # combined_df = combined_df.set_index('台番')

    return combined_df

def data_shaping_for_summary(df):
    df["差枚_mean"] = round(df["差枚_mean"],1)
    df["G数_mean"] = round(df["G数_mean"],1)
    df["BB_mean"] = round(df["BB_mean"],1)
    df["RB_mean"] = round(df["RB_mean"],1)
    
    df["BB確率"] = round(df["G数_sum"] / df["BB_sum"],1)
    df["RB確率"] = round(df["G数_sum"] / df["RB_sum"],1)
    df["合成確率"] = round(df["G数_sum"] / ( df["BB_sum"] + df["RB_sum"] ),1)
    df["payout"] = round(((df["G数_sum"]*3 + df["差枚_sum"]) / (df["G数_sum"]*3))*100,1)

    return df

def summary_by_machine(df):
    # 機種単位でグループ化して集約
    aggregated = df.groupby("機種").agg({
        "差枚": ["sum", "mean"],
        "G数": ["sum", "mean"],
        "BB": ["sum", "mean"],
        "RB": ["sum", "mean"]
    })

    # カラム名のフラット化（必要に応じて）
    aggregated.columns = ['_'.join(col).strip() for col in aggregated.columns]
    aggregated.reset_index(inplace=True)

    # 機種単位のデータ数を追加
    aggregated['台数'] = df.groupby("機種").size().values
    # "差枚"が0より大きいデータの数を追加
    aggregated['勝ち'] = df[df["差枚"] > 0].groupby("機種").size().reindex(aggregated["機種"], fill_value=0).values

    aggregated = data_shaping_for_summary(aggregated)

    # カラムの並び替え（必要に応じて）
    column_order = ["機種", "勝ち", "台数", "差枚_mean", "G数_mean",
                    "BB確率", "RB確率", "合成確率", "payout",
                    "差枚_sum", "G数_sum", "BB_sum", "RB_sum", "BB_mean", "RB_mean"]
    aggregated = aggregated[column_order]

    return aggregated

def summary_by_machine_no(df):
    # 台番単位でグループ化して集約
    aggregated = df.groupby(["台番"]).agg({
        "差枚": ["sum", "mean"],
        "G数": ["sum", "mean"],
        "BB": ["sum", "mean"],
        "RB": ["sum", "mean"]
    })

    # カラム名のフラット化（必要に応じて）
    aggregated.columns = ['_'.join(col).strip() for col in aggregated.columns]
    aggregated.reset_index(inplace=True)

    # 機種単位のデータ数を追加
    aggregated['台数'] = df.groupby(["台番"]).size().values
    # "差枚"が0より大きいデータの数を追加
    aggregated['勝ち'] = df[df["差枚"] > 0].groupby(["台番"]).size().reindex(aggregated["台番"], fill_value=0).values

    aggregated = data_shaping_for_summary(aggregated)

    # カラムの並び替え（必要に応じて）
    column_order = ["台番", "勝ち", "台数", "差枚_mean", "G数_mean",
                    "BB確率", "RB確率", "合成確率", "payout",
                    "差枚_sum", "G数_sum", "BB_sum", "RB_sum", "BB_mean", "RB_mean"]
    aggregated = aggregated[column_order]

    return aggregated

def summary_by_date(df):
    # 日付単位でグループ化して集約
    aggregated = df.groupby("日付").agg({
        "差枚": ["sum", "mean"],
        "G数": ["sum", "mean"],
        "BB": ["sum", "mean"],
        "RB": ["sum", "mean"]
    })

    # カラム名のフラット化（必要に応じて）
    aggregated.columns = ['_'.join(col).strip() for col in aggregated.columns]
    aggregated.reset_index(inplace=True)

    # 機種単位のデータ数を追加
    aggregated['台数'] = df.groupby("日付").size().values
    # "差枚"が0より大きいデータの数を追加
    aggregated['勝ち'] = df[df["差枚"] > 0].groupby("日付").size().reindex(aggregated["日付"], fill_value=0).values

    aggregated = data_shaping_for_summary(aggregated)

    # カラムの並び替え（必要に応じて）
    column_order = ["日付", "勝ち", "台数", "差枚_mean", "G数_mean",
                    "BB確率", "RB確率", "合成確率", "payout",
                    "差枚_sum", "G数_sum", "BB_sum", "RB_sum", "BB_mean", "RB_mean"]
    aggregated = aggregated[column_order]

    return aggregated

def summary_data_frame(df):
    df["BB確率"] = round(df["G数"] / df["BB"],1)
    df["RB確率"] = round(df["G数"] / df["RB"],1)
    df["合成確率"] = round(df["G数"] / ( df["BB"] + df["RB"] ),1)
    df["payout"] = round(((df["G数"]*3 + df["差枚"]) / (df["G数"]*3))*100,1)

    # カラムの並び替え（必要に応じて）
    column_order = ["日付","台番","機種", "差枚", "G数", "BB", "RB",
                    "BB確率", "RB確率", "合成確率", "payout"]
    df = df[column_order]

    return df

def get_pivoted_by_machine_no(df):
    dates = sorted(df["日付"].drop_duplicates().tolist(), reverse=True)
    columns = ["機種", "差枚", "G数"]
    desired_order = [f"{col}_{date.strftime('%Y-%m-%d')}" for date in dates for col in columns]

    pivoted = df.pivot(index="台番", columns="日付", values=["機種", "差枚", "G数"])
    pivoted.columns = [f"{col[0]}_{col[1].strftime('%Y-%m-%d')}" for col in pivoted.columns]
    pivoted = pivoted[desired_order]

    return pivoted

def get_pivoted_by_machine(df):
    # "機種","日付"単位で"差枚","G数"の平均値を計算
    mean_values = df.groupby(["機種", "日付"])[["差枚", "G数"]].mean().reset_index()

    # "機種","日付"単位のデータ数をカウント
    data_count = df.groupby(["機種", "日付"]).size().reset_index(name="台数")

    # "機種","日付"単位で"差枚"が0より大きいデータ数をカウント
    positive_count = df[df["差枚"] > 0].groupby(["機種", "日付"]).size().reset_index(name="勝ち")

    # 結果を結合
    aggregated = mean_values.merge(data_count, on=["機種", "日付"])
    aggregated = aggregated.merge(positive_count, on=["機種", "日付"], how="left")
    aggregated["勝ち"] = aggregated["勝ち"].fillna(0).astype(int)  # NaNを0に変換

    # 差枚、G数をround
    aggregated["差枚"] = round(aggregated["差枚"],1)
    aggregated["G数"] = round(aggregated["G数"],1)

    dates = sorted(aggregated["日付"].drop_duplicates().tolist(), reverse=True)
    columns = ["勝ち", "台数", "差枚", "G数"]
    desired_order = [f"{col}_{date.strftime('%Y-%m-%d')}" for date in dates for col in columns]

    pivoted = aggregated.pivot(index="機種", columns="日付", values=["勝ち", "台数", "差枚", "G数"])
    pivoted.columns = [f"{col[0]}_{col[1].strftime('%Y-%m-%d')}" for col in pivoted.columns]
    pivoted = pivoted[desired_order]

    return pivoted

def scrape_one_day(target_url):
    # Get links from the main page
    links = get_links_from_main_page(target_url)
    # st.write(f"複数設置機種のリンクを取得しました: {len(links)}件")

    combined_df = pd.DataFrame()
    # Scrape each detail page
    for link in links:
        df = scrape_detail_page(link)
        combined_df = pd.concat([combined_df, df])

    # Get links from the main page
    links = get_links_from_main_page_variety(target_url)
    # st.write(f"少数設置機種のリンクを取得しました: {len(links)}件")

    # Scrape each detail page
    for link in links:
        df = scrape_detail_page_variety(link)
        combined_df = pd.concat([combined_df, df])
    
    return combined_df

def get_dict_url():
    dict_url = {
        "ビックマーチ東習志野":"https://www.slorepo.com/hole/e38393e38383e382afe3839ee383bce38381e69db1e7bf92e5bf97e9878ee5ba97code/",
        "楽園松戸":"https://www.slorepo.com/hole/e6a5bde59c92e69dbee688b8e5ba97code/",
        "楽園柏":"https://www.slorepo.com/hole/e6a5bde59c92e69f8fe5ba97code/",
        "エスパス稲毛海岸":"https://www.slorepo.com/hole/e382a8e382b9e38391e382b9e697a5e68b93e7a8b2e6af9be9a785e5898de696b0e9a4a8code/",
        "サンラッキー市川":"https://www.slorepo.com/hole/e382b5e383b3e383a9e38383e382ade383bce5b882e5b79de5ba97code/",
        "ジュラク柏":"https://www.slorepo.com/hole/e382b8e383a5e383a9e382afe69f8fe5ba97code/",
        "稲毛海岸UNO":"https://www.slorepo.com/hole/e7a8b2e6af9be6b5b7e5b2b8554e4fcode/",
        "八柱UNO":"https://www.slorepo.com/hole/e585abe69fb1554e4fcode/",
        "南柏UNO":"https://www.slorepo.com/hole/e58d97e69f8f554e4fcode/",
        "本八幡UNO":"https://www.slorepo.com/hole/e69cace585abe5b9a1554e4fcode/",
        "本八幡ZORON":"https://www.slorepo.com/hole/e69cace585abe5b9a15a6f526f4ecode/",
        "サンラッキー市川":"https://www.slorepo.com/hole/e382b5e383b3e383a9e38383e382ade383bce5b882e5b79de5ba97code/",
        "エクスアリーナ柏":"https://www.slorepo.com/hole/e382a8e382afe382b9e382a2e383aae383bce3838ae69f8fcode/",
        "戸越ミナト":"https://www.slorepo.com/hole/e688b8e8b68ae3839fe3838ae38388code/"
    }
    return dict_url

def is_exist_url(url):
    flag = True
    try:
        f = urllib.request.urlopen(url)
        f.close()
    except:
        flag = False
        print ("NotFound:" + url)
    return flag