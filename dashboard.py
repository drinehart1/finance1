"""
CREATED: 30-JUL-2021
LAST EDIT: 30-JUL-2021
AUTHOR: DUANE RINEHART, MBA (duane.rinehart@gmail.com)

ADMIN FOR ROBO ADVISOR
"""

try:
    import data_access
    from data_access import YahooAPI, HistData
except ImportError:
    raise ImportError("ERROR LOADING PREREQUISITE: data_access")

y = YahooAPI()
hist = HistData()


def populate_db():
    # ASSUMPTIONS - CAPTURE 1 YEAR OF HISTORICAL DATA ("1y")
    # SELECTION OF FUNDS LIMITED TO ETF

    # MSFT, SPY, AAAU, VCIT : (MICROSOFT, SP500, GOLD ETF, BOND ETF)
    symbol = "VCIT"
    period = "1y"

    hist_data = y.capture_historical(symbol, period)
    # print(hist_data.columns) - show column headers [for testing]
    for index, row in hist_data.iterrows():
        result_date = index.to_pydatetime().date()
        sql = """INSERT OR IGNORE INTO robo (date, symbol, close)
                         VALUES ('{}', '{}', '{}')
                      """.format(
            result_date,
            symbol,
            row["Close"],
        )
        hist.qry(sql, rtn_results=False)
    print("FINISHED POPULATING DB WITH SYMBOL: ", symbol)


def db_stats():
    sql = """
    SELECT Symbol, MIN(date), MAX(date) 
    FROM robo 
    GROUP BY symbol 
    ORDER BY symbol ASC
    """
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
