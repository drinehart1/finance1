"""
CREATED: 30-JUL-2021
LAST EDIT: 22-DEC-2024
AUTHOR: DUANE RINEHART, MBA (duane.rinehart@gmail.com)

ADMIN FOR ROBO ADVISOR & OPTION TRADER
"""

try:
    import data_access
    from data_access import YahooAPI, HistData
except ImportError:
    raise ImportError("ERROR LOADING PREREQUISITE: data_access")


def populate_db(db_server: str, db_name: str, db_table: str, symbols = None, period: str = '1y'):
    # ASSUMPTIONS - CAPTURE 1 YEAR OF HISTORICAL DATA ("1y")
    # SELECTION OF FUNDS LIMITED TO ETF
    # period: intervals are: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max

    y = YahooAPI()
    hist = HistData(db_server, db_name)

    for symbol in symbols:
        hist_data = y.capture_historical(symbol, period)

    # print(hist_data.columns) #- show column headers [for testing]
        for index, row in hist_data.iterrows():
            result_date = index.to_pydatetime().date()
            sql = f"""INSERT OR IGNORE INTO {db_table} (date, symbol, open, close, high, low, volume)
                        VALUES ('{result_date}', '{symbol}', '{row["Open"]}', '{row["Close"]}', '{row["High"]}', '{row["Low"]}', '{row["Volume"]}')
                    """
            # print(sql)
            hist.qry(sql, rtn_results=False)
        print(f"FINISHED POPULATING DB WITH SYMBOL: {symbol} for period: {period}")


def db_table_stats(db_server: str, db_name: str, db_table: str):
    hist = HistData(db_server, db_name)

    sql = '''SELECT symbol, MIN(date) AS start_date, MAX(date) AS end_date
        FROM history
        GROUP BY symbol
        ORDER BY symbol;'''
    results = hist.qry(sql, rtn_results=True)
    return results


def db_stats(db_server: str, db_name: str, db_table: str):
    sql = """
    SELECT Symbol, MIN(date), MAX(date) 
    FROM robo 
    GROUP BY symbol 
    ORDER BY symbol ASC
    """

    y = YahooAPI()
    hist = HistData(db_server, db_name)

    results = hist.qry(sql, rtn_results=True)
    print(
        "{symbol:<6}\t{start:<10}\t{end:<10}".format(
            symbol="SYMBOL", start="START_DATE", end="END_DATE"
        )
    )
    for row in results:
        symbol, start, end = row
        print(
            "{symbol:<6}\t{start:<10}\t{end:<10}".format(
                symbol=symbol, start=start, end=end
            )
        )


def display_menu():
    print("Welcome to Robo Advisor Admin")
    print("1. Populate DB")
    print("2. Get DB Stats")
    print("X. Exit")


def main():
    display_menu()
    hist = HistData()
    y = YahooAPI()

    while True:
        command = input("Command: ")
        if command == "1":
            populate_db()
        elif command == "2":
            db_stats()
        # elif command == "drop":
        #     drop_item(inventory)
        elif command.upper() == "X":
            break
        else:
            print("Not a valid command. Please try again.\n")
    print("Bye!")


if __name__ == "__main__":
    main()
