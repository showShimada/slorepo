
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import quote, urljoin


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
    df = pd.read_html(str(table))[0]

    # Set index to "台番" and drop "平均" row
    df = df.set_index('台番')
    df = df[df.index != '平均']
    df = df.drop(columns='合成')

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

        df = pd.read_html(str(table))[0]

        # Set index to "台番" and drop "平均" row
        df = df.drop(columns='合成')
        df['台番'] = machine_no

        # Add columns for "機種" and "日付"
        df['機種'] = machine
        df['日付'] = date
        df['日付'] = df['日付'].str.replace(r'\([^\)]*\)', '', regex=True)
        df['日付'] = pd.to_datetime(df['日付'], format='%Y/%m/%d')

        combined_df = pd.concat([combined_df, df])

    combined_df = combined_df.set_index('台番')

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
    # aggregated["差枚_mean"] = round(aggregated["差枚_mean"],1)
    # aggregated["G数_mean"] = round(aggregated["G数_mean"],1)
    # aggregated["BB_mean"] = round(aggregated["BB_mean"],1)
    # aggregated["RB_mean"] = round(aggregated["RB_mean"],1)
    
    # aggregated["BB確率"] = round(aggregated["G数_sum"] / aggregated["BB_sum"],1)
    # aggregated["RB確率"] = round(aggregated["G数_sum"] / aggregated["RB_sum"],1)
    # aggregated["合成確率"] = round(aggregated["G数_sum"] / ( aggregated["BB_sum"] + aggregated["RB_sum"] ),1)
    # aggregated["payout"] = round(((aggregated["G数_sum"]*3 + aggregated["差枚_sum"]) / (aggregated["G数_sum"]*3))*100,1)

    # カラムの並び替え（必要に応じて）
    column_order = ["機種", "勝ち", "台数", "差枚_mean", "G数_mean",
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
    # aggregated["差枚_mean"] = round(aggregated["差枚_mean"],1)
    # aggregated["G数_mean"] = round(aggregated["G数_mean"],1)
    # aggregated["BB_mean"] = round(aggregated["BB_mean"],1)
    # aggregated["RB_mean"] = round(aggregated["RB_mean"],1)
    
    # aggregated["BB確率"] = round(aggregated["G数_sum"] / aggregated["BB_sum"],1)
    # aggregated["RB確率"] = round(aggregated["G数_sum"] / aggregated["RB_sum"],1)
    # aggregated["合成確率"] = round(aggregated["G数_sum"] / ( aggregated["BB_sum"] + aggregated["RB_sum"] ),1)
    # aggregated["payout"] = round(((aggregated["G数_sum"]*3 + aggregated["差枚_sum"]) / (aggregated["G数_sum"]*3))*100,1)

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
    column_order = ["機種", "差枚", "G数", "BB", "RB",
                    "BB確率", "RB確率", "合成確率", "payout"]
    df = df[column_order]

    return df