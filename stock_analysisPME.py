"""
CREATED: 3-JUN-2021
LAST EDIT: 3-JAN-2025
AUTHOR: DUANE RINEHART, MBA (duane.rinehart@gmail.com)

READS blotter.xlsx (SYMBOL,	SHARES,	UNITARY, EXTENDED, DATE, BROKER, EXIT_TARGET)
COMPARES holding period to SP500 performance ($, days) using PME (Public Market Equivalent) ref: https://docs.preqin.com/reports/Preqin-Special-Report-PME-July-2015.pdf

REF: https://towardsdatascience.com/python-for-finance-stock-portfolio-analyses-6da4c3e61054
"""
import os
import pandas as pd
from datetime import datetime as dt
import sqlite3
import yfinance as yf

# import numpy as np
# import matplotlib.pyplot as plt
# import plotly.graph_objs as go

try:
    import constants

except ImportError:
    raise ImportError("ERROR LOADING PREREQUISITE [FROM WORKING DIRECTORY]: constants")


class HistData:
    """
    METHODS FOR CRUD OPERATIONS OF HISTORICAL DATA
    """

    _db_server = constants.HIST_DB_SERVER
    _db_name = constants.HIST_DB_NAME

    def __init__(self):
        """
        INIT CONNECTION TO DATABASE; IMPORTS SCHEMA IF NOT EXISTS
        """
        if self._db_server == "sqlite":
            self._con = sqlite3.connect(self._db_name)

        try:
            self._cur = self._con.cursor()
        except:
            print(
                "UNABLE TO CONNECT TO DATABASE: \n",
                "TYPE:",
                self._db_server + "\n",
                "HOST (FILENAME IF SQLITE):",
                self._db_name,
            )
        # finally:
        #     self._con.close()

        # CHECK IF sp500 TABLE EXISTS
        self._cur.execute(
            """SELECT
                COUNT(name)
                FROM
                sqlite_master
                WHERE
                type = 'table'
                AND
                name = 'sp500'"""
        )

        if self._cur.fetchone()[0] != 1:
            print("INITIALIZE DB...")
            try:
                sql_file = open(constants.HIST_DB_SCHEMA)
                sql_as_string = sql_file.read()
                self._cur.executescript(sql_as_string)
            except FileNotFoundError:
                print(
                    "DATABASE SCHEMA CREATION FILE MISSING:", constants.HIST_DB_SCHEMA
                )

    def qry(self, sql, rtn_results: bool = True, rtn_iterator: bool = False) -> tuple:
        self._cur.execute(sql)
        if rtn_results == True:
            return self._cur.fetchall()
        else:
            self._con.commit()


class YahooAPI:
    """
    METHODS FOR SCRAPING YAHOO FINANCE
    ref: https://aroussi.com/post/python-yahoo-finance
    """

    def capture_historical(self, strTicker: str, p):
        stock = yf.Ticker(strTicker)
        d = stock.history(period=p)
        df = pd.DataFrame(data=d)
        return df  # RETURN DATAFRAME OF ALL HISTORICAL [RAW] QUOTES


class DataAccess:
    """
    METHODS FOR EXTRACTING & MANIPULATING RAW DATA
    """

    def __init__(self):
        self._srcPath = constants.SRCPATH
        self._srcFile = constants.SRCFILE

    def extract_blotter_data(self):
        infile = os.path.join(self._srcPath, self._srcFile)
        return pd.read_excel(infile, sheet_name="master")

    def extract_desc_var(self, df):
        """
        EXTRACT DESCRIPTIVE DATA FROM [BLOTTER] DATAFRAME
        """
        min = df["DATE"].min().to_pydatetime().date()
        max = df["DATE"].max().to_pydatetime().date()
        cur_year = dt.today().year
        end_of_last_year = dt(year=cur_year - 1, month=12, day=31).date()
        diff = (max - min).days
        return min, max, diff, end_of_last_year


def pop_sp500_tables(hist, diff):
    """
    SCRAPES YAHOO FINANCE ('^GSPC' IS S&P500 SYMBOL) TO DOWNLOAD HISTORICAL SP500 DATA AND INSERTS INTO DATABASE

    Valid periods are: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    """
    y = YahooAPI()
    if diff < 31:
        period = "1mo"
    elif diff < 91:
        period = "3mo"
    elif diff < 181:
        period = "6mo"
    elif diff < 365:
        period = "1y"
    elif diff < 730:
        period = "2y"

    hist_data = y.capture_historical(
        "^GSPC", period
    )  # NOTE RETURNED DATA IS OF TYPE PANDAS DATAFRAME

    for index, row in hist_data.iterrows():
        result_date = index.to_pydatetime().date()

        sql = """INSERT OR IGNORE INTO sp500 (date, open, close, high, low, volume)
                 VALUES ('{}', '{}', '{}', '{}', '{}', '{}')
              """.format(
            result_date,
            row["Open"],
            row["Close"],
            row["High"],
            row["Low"],
            row["Volume"],
        )
        # NOTE: USING 'date' AS PRIMARY KEY PREVENTS DUPLICATE ENTRIES
        # THIS WILL STILL PRODUCE INTEGRITY ERROR - WORKAROUND ADD IGNORE TO SQL
        # REF: https://stackoverflow.com/questions/36518628/sqlite3-integrityerror-unique-constraint-failed-when-inserting-a-value
        hist.qry(sql, rtn_results=False)


def main():
    data = DataAccess()
    xl_df = data.extract_blotter_data()
    min, max, diff, prev_year_end = data.extract_desc_var(xl_df)
    hist = HistData()

    # QRY FOR DATA COVERING TIME PERIOD OF INTEREST
    SQL = "SELECT COUNT(*) FROM sp500 WHERE date >= '{}' AND date <= '{}' ORDER BY date ASC".format(
        min, max
    )
    cnt = hist.qry(SQL)  # RETURNS LIST OF TUPLES

    datapoints = cnt[0][0]  # CAPTURE FIRST ELEMENT OF LIST; FIRST ELEMENT OF TUPLE
    if diff > 0:
        if (
            datapoints / diff < 0.65
        ):  # < 65%; PULL MORE DATA [NOTE: 71.4% OF DATES ARE M-F 5/7 DAYS PER WEEK; (EXCLUDES HOLIDAYS)]
            pop_sp500_tables(hist, diff)
        else:
            print(
                "CONTINUE WITH ",
                round(datapoints / diff * 100, 2),
                "% of DATES (INCLUDES HOLIDAYS & WEEKENDS)",
            )
            # results = hist.qry(SQL, rtn_iterator=True)  # RETURNS LIST OF TUPLES


if __name__ == "__main__":
    main()
