"""
CREATED: 30-JUL-2021
LAST EDIT: 5-NOV-2021
AUTHOR: DUANE RINEHART, MBA (duane.rinehart@gmail.com)

CREATE ROBO ADVISOR APP TO RECOMMEND STOCK SECTOR INVESTMENTS BASED ON INPUT CRITERIA (1ST ITERATION)
-CREATE POSSIBLE PORTFOLIOS, SCORE BASED ON SELECTED CRITERIA (INVESTMENT TIME HORIZON, CAPITAL, RISK TOLERANCE)
-INITIAL INVESTMENTS ARE BASED ON SECTOR ETF FUNDS



REF: https://portfolioconstructs.com/blog-detail/18?title=How%20I%20Built%20a%20Robo-Advisor%20Website%20from%20Scratch
video: https://www.youtube.com/watch?v=T-oCi0R0NOI (but does not want to give all secrets away)
public notes:
-Our tool heavily weights Expense Ratio, Liquidity and Market Capitalization.
-output fields: Symbol	Name	Asset Class	Expense Ratio	Price	# of Shares	Total Amount (overall)
-annual: Dividend Yield	Dividend Amount	Expense Ratio	Expense Amount
-previous return: One Week Return	One Month Return	One Year Return	Five Year Return (historicals)
(including classes - equity, bond, commodity, real estate, cash)
DATA PROVIDERS: IEX Cloud, Yahoo Finance, Alpha Vantage
"""

try:
    import data_access
except ImportError:
    raise ImportError("ERROR LOADING PREREQUISITE: data_access")


def populate_db(symbol):
    pass


def main():
    # CAPTURE INPUTS
    horizon = input("Time horizon (years): ")
    y0_value = input("Starting portfolio value ($): ")
    risk_tol = input("Risk tolerance (1-5) 1=low,5=high: ")

    print(horizon, y0_value, risk_tol)

    # MODERN PORTFOLIO THEORY DEPENDS ON EXPECTED RETURNS
    # NEED DATA SOURCE FOR EXPECTED RETURN BY ETF
    # JUL ASSUMPTIONS:
    # RETURN: EQUITY (8.0% - SP500), COMMODITY (5.0% - GOLD), MSFT[EQUITY2] (8.5% - SP500), BOND INDEX (4.5%)
    # RISK (STANDARD DEVIATION): 30%,16%,33%,14%
    # MIN WEIGHT - 15%
    # MAX WEIGHT - 35%
    # INITIAL WEIGHT WILL BE 1/5 (TOTAL CLASSES) = 20%

    # WILL REQUIRE COVARIANCE MATRIX (HOW EACH ASSET CLASS RELATES TO OTHER ASSET CLASSES)
    # AVAILABLE HERE? - https://admainnew.morningstar.com/webhelp/Practice/Plans/Correlation_Matrix_of_the_14_Asset_Classes.htm
    # EXCEL - ANALYSIS, SOLVER TOOL PACKS
    # REQUIRES PRICES FOR EACH ASSET FOR PREVIOUS YEAR


if __name__ == "__main__":
    main()
