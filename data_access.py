import constants
import os
import pandas as pd
from datetime import datetime as dt
import sqlite3
import yfinance as yf


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

        # CHECK IF robo TABLE EXISTS
        self._cur.execute(
            """SELECT
                COUNT(name)
                FROM
                sqlite_master
                WHERE
                type = 'table'
                AND
                name = 'robo'"""
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

    def capture_historical(self, ticker, p):
        stock = yf.Ticker(ticker)
        d = stock.history(period=p)
        df = pd.DataFrame(data=d)
        return df  # RETURN DATAFRAME OF ALL HISTORICAL [RAW] QUOTES

    def capture_historical2(self, tickers, p):  # MULTIPLE TICKERS (MORE EFFICIENT)
        d = yf.download(tickers, period=p)
        df = pd.DataFrame(data=d)
        return df
