# SRC: https://github.com/mariostoev/finviz

# CREATED: 30-OCT-2020
# LAST EDIT: 16-MAY-2022
# AUTHOR: DUANE RINEHART, MBA (duane.rinehart@gmail.com)

# IMPLEMENTS API CONNECTION TO STOCK INFORMATION SERVICE FINVIZ FOR PURPOSES OF STOCK SCREENING

# REQUIRES:
# - PYTHON 3.5+

# LOAD PREREQUISITES
import symtable

try:
    import constants

except ImportError:
    raise ImportError("ERROR LOADING PREREQUISITE: constants")

try:
    import finviz

except ImportError:
    print("ERROR LOADING PREREQUISITE: finviz")
    exit()

try:
    import os
    import time
    import concurrent.futures as cf
    from datetime import datetime
    import pandas as pd
    import xlsxwriter

    # from finviz.screener import Screener
    # from urllib.request import urlopen
    # import json
    # import csv


except ImportError:
    print("ERROR LOADING PREREQUISITES")
    exit()

# GLOBAL VARIABLES
stock_data = []
analyst_data = []


def load_stock_list():
    """read from blotter.xlsx, which contains [at a minimum] the following fields:
    "SYMBOL", "SHARES", "UNITARY", "BROKER", "EXIT_TARGET"

    :return: Array of current holdings
    :rtype: Pandas dataframe
    """    
    if os.name == "nt":
        infile = os.path.join(constants.outpath, "blotter.xlsx")
    else:
        infile = os.path.join(constants.outpath_linux, "blotter.xlsx")

    return pd.read_excel(infile, sheet_name="master")


def lookup(stock):
    stock_data.append(finviz.get_stock(stock))

    analyst_raw = {}
    analyst_raw["symbol"] = stock
    analyst_raw["info"] = finviz.get_analyst_price_targets(stock)
    analyst_data.append(analyst_raw)
    # analyst_data.update(finviz.get_analyst_price_targets(stock)[0])
    # print(str(analyst_data))


def main(output):
    xl_df = load_stock_list()
    stock_list = xl_df["SYMBOL"].unique()  # DEDUPLICATE
    stock_list = xl_df["SYMBOL"].values.tolist()
    # stock_list = list(dict.fromkeys(stock_list))

    with cf.ThreadPoolExecutor() as executor:  # AUTO-JOINS PROCESSES (WAITS FOR PROCESSES TO COMPLETE BEFORE CONTINUING WITH SCRIPT)
        for stock in stock_list:
            f1 = executor.submit(
                lookup(stock)
            )  # SCHEDULES METHOD FOR EXECUTION AND RETURNS FUTURE OBJECT

    df = pd.DataFrame(data=stock_data)
    df.insert(
        loc=0, column="symbol", value=stock_list
    )  # ADD SYMBOLS TO BEGINNING OF DATAFRAME

    # SAVE RAW STOCK DATA IN WORKSHEET 'raw_data'
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="raw_data")
    workbook = writer.bookworksheet = writer.sheets["raw_data"]

    analyst = pd.DataFrame(data=analyst_data)
    analyst.to_excel(writer, index=False, sheet_name="analysts")
    workbook = writer.bookworksheet = writer.sheets["analysts"]

    # MERGE DATAFRAMES PRIOR TO SAVE
    df2 = df[
        ["symbol", "Price", "Dividend", "Dividend %"]
    ]  # EXTRACT SPECIFIC COLUMNS FOR ANALYSIS
    input_stock_list = pd.DataFrame(
        xl_df, columns=["SYMBOL", "SHARES", "UNITARY", "BROKER", "EXIT_TARGET"]
    )
    mergeDf = pd.merge(input_stock_list, df2, left_on="SYMBOL", right_on="symbol")
    del mergeDf["symbol"]

    mergeDf["Price"] = mergeDf["Price"].astype(float)
    mergeDf["Dividend %"] = mergeDf["Dividend %"].replace("%", "", regex=True)
    mergeDf["Dividend %"] = mergeDf["Dividend %"].replace("-", 0, regex=True)
    mergeDf["Dividend %"] = mergeDf["Dividend %"].astype(float)
    mergeDf["Dividend %"] = mergeDf["Dividend %"] / 100

    mergeDf["Dividend %"] = mergeDf["Dividend %"].astype(float)
    mergeDf["ROI"] = (
        (mergeDf["Price"] - mergeDf["UNITARY"]) / mergeDf["UNITARY"]
    ).astype(float)

    mergeDf = mergeDf.sort_values(by="ROI", ascending=False)
    # SAVE ANALYSIS DATA IN WORKSHEET 'analysis'
    mergeDf.to_excel(writer, sheet_name="analysis", index=False)

    # ADDITIONAL COLUMN FORMATTING ['analysis' WORKSHEET]
    workbook = writer.book
    worksheet = writer.sheets["analysis"]
    format2 = workbook.add_format({"num_format": "0.00%"})
    worksheet.set_column("H:I", None, format2)

    # PORTFOLIO ANALYSIS
    port1 = df[["symbol", "Sector", "Price"]]  # EXTRACT SPECIFIC COLUMNS FOR ANALYSIS
    port2 = pd.DataFrame(xl_df, columns=["SYMBOL", "SHARES"])
    mergePort = pd.merge(port2, port1, left_on="SYMBOL", right_on="symbol")
    del mergePort["symbol"]

    mergePort["Price"] = mergePort["Price"].astype(float)
    mergePort["NAV"] = (mergePort["Price"] * mergePort["SHARES"]).astype(float)
    mergePort.to_excel(writer, sheet_name="portfolio", index=False)

    # SUBTOTALS BY SECTOR
    mergePort.sort_values("Sector", inplace=True)
    portfolio_NAV_by_sector = (
        mergePort.groupby("Sector")["NAV"].sum().reset_index(name="ACCUMULATION")
    )
    portfolio_NAV_by_sector["ACCUMULATION_PCT"] = (
        portfolio_NAV_by_sector["ACCUMULATION"]
        / portfolio_NAV_by_sector["ACCUMULATION"].sum()
    )
    portfolio_NAV_by_sector.to_excel(
        writer, sheet_name="portfolio_breakdown", index=False
    )

    workbook = writer.book
    worksheet = writer.sheets["portfolio_breakdown"]
    format2 = workbook.add_format({"num_format": "0.00%"})
    worksheet.set_column("C:C", None, format2)

    format1 = workbook.add_format({"num_format": "0.00"})
    workbook = writer.book
    worksheet = writer.sheets["portfolio"]
    worksheet.set_column("D:E", None, format1)
    writer.save()

    # NEED TO GET SUBTOTALS BY SECTOR, % PORTFOLIO BY SECTOR

    # finviz.get_analyst_price_targets('AAPL')
    # filters = ['fa_div_pos', #POSITIVE DIVIDEND YIELD
    #           'fa_payoutratio_pos', #POSITIVE DIVIDENT PAYOUT RATIO
    #           'sh_avgvol_o200', #AVG VOLUME >200K
    #           'sh_curvol_o200'] #CUR_VOLUME >200K

    # stock_list = Screener(filters=filters, table='Performance', order='change')  # Get the performance table and sort it by price ascending

    # Export the screener results to .csv
    # stock_list.to_csv("stock.csv")

    # Create a SQLite database
    # stock_list.to_sqlite("stock.sqlite3")

    # for stock in stock_list[0:50]:  # Loop through 10th - 20th stocks
    #    print(stock['Ticker'], stock['Price'], stock['Change']) # Print symbol and price

    # Add more filters
    # stock_list.add(filters=['fa_div_high'])  # Show stocks with high dividend yield
    # or just stock_list(filters=['fa_div_high'])

    # Print the table into the console
    # print(stock_list)


if __name__ == "__main__":
    start = time.perf_counter()
    print("SCRIPT NAME:", os.path.basename(__file__))
    now = datetime.now()  # datetime object containing current date and time
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    print("SCRIPT START TIMESTAMP:", dt_string)

    if os.name == "nt":
        OUTPATH = constants.outpath
    else:
        OUTPATH = constants.outpath_linux

    os.chdir(OUTPATH)
    out_dir = os.path.join(OUTPATH, constants.outfile)
    print("CURRENT PATH:", os.getcwd())
    print("OUTPUT DESTINATION:", os.path.join(OUTPATH, constants.outfile))

    main(out_dir)

    now = datetime.now()  # datetime object containing current date and time
    dt_string = now.strftime("%m-%d-%Y %H:%M:%S")
    print("SCRIPT END TIMESTAMP:", dt_string)
    finish = time.perf_counter()
    print(f"EXECUTION TIME: {round(finish-start,2)}s")
