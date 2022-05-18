# *** DEFINE CONSTANTS ***
# DO NOT ADD TO VERSION CONTROL AFTER ENTERING PERSONAL INFO

# LOCATION WHERE BLOTTER FILE IS LOCATED (INPUT)
SRCPATH = "D:/financial/"
SRCFILE = "blotter.xlsx"

# OUTPUT DATA DESTINATION (WINDOWS FORMAT)
outpath = "D://financial//"
outpath_linux = "/mnt/d/financial/"

# OUTPUT FILE NAMES
outfile = "stock_data_output.xlsx"
out_screener = "screener_output.xlsx"

# **ROBOADVISOR DEFAULTS (OVERRIDDEN IN APP)
# DATABASE FOR HISTORICAL STOCK INFO (USED BY stock_analysisPME)
HIST_DB_SERVER = "sqlite"
HIST_DB_NAME = "hist.db"
HIST_DB_SCHEMA = "db_schema.sql"

# RULES FOR DIVERSIFICATION & RISK (AS PERCENTAGE OF TOTAL PORTFOLIO)
max_sector_pct = 0.2
max_stock_pct = 0.1

# INTERNAL DISCOUNT RATE (WHAT OPPORTUNITY COST OF INVESTED FUNDS)
discount_rate = 0.12
