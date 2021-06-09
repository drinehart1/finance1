"""
CREATED: 3-JUN-2021
LAST EDIT: 9-JUN-2021
AUTHOR: DUANE RINEHART, MBA (duane.rinehart@gmail.com)

READS blotter.xlsx (SYMBOL,	SHARES,	UNITARY, EXTENDED, DATE, BROKER, EXIT_TARGET)
COMPARES holding period to SP500 performance ($, days) using PME (Public Market Equivalent) ref: https://docs.preqin.com/reports/Preqin-Special-Report-PME-July-2015.pdf

REF: https://towardsdatascience.com/python-for-finance-stock-portfolio-analyses-6da4c3e61054
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime as dt
import sqlite3

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
        INIT CONNECTION TO DATABASE
        """
        if self._db_server == "sqlite":
            _con = sqlite3.connect(self._db_name)

        try:
            _cur = _con.cursor()
        except:
            print(
                "UNABLE TO CONNECT TO DATABASE: \n",
                "TYPE:",
                self._db_server + "\n",
                "HOST (FILENAME IF SQLITE):",
                self._db_name,
            )

        try:
            _cur.execute(
                """SELECT
                name
                FROM
                sqlite_master
                WHERE
                type = 'table'
                AND
                name = '{table_name}'.format('sp500')"""
            )
        except:
            print("INITIALIZE DB...")
            try:
                sql_file = open(constants.HIST_DB_SCHEMA)
                sql_as_string = sql_file.read()
                _cur.executescript(sql_as_string)
            except FileNotFoundError:
                print(
                    "DATABASE SCHEMA CREATION FILE MISSING:", constants.HIST_DB_SCHEMA
                )

            # print("ADDING 'sp500' TABLE")
            # _cur.execute(
            #     """CREATE TABLE IF NOT EXISTS sp500 (
            #         `date` datetime NOT NULL PRIMARY KEY,
            #         `open` DECIMAL NOT NULL,
            #         `close` DECIMAL NOT NULL,
            #         `high` DECIMAL NOT NULL,
            #         `low` DECIMAL NOT NULL,
            #         `volume` INT NOT NULL
            #     );"""
            # )

    def qry(self, sql, rtn_results: bool = True) -> tuple:
        pass


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
        return min, max, end_of_last_year


def main():
    data = DataAccess()
    xl_df = data.extract_blotter_data()
    # print(xl_df[["SYMBOL", "EXTENDED", "DATE"]])
    min, max, prev_year_end = data.extract_desc_var(xl_df)

    print(min, max, prev_year_end, sep="\n")
    hist = HistData()


if __name__ == "__main__":
    main()
