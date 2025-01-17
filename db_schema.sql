CREATE TABLE IF NOT EXISTS sp500 (
	`date` datetime NOT NULL PRIMARY KEY,
	`open` DECIMAL NOT NULL,
	`close` DECIMAL NOT NULL,
	`adj_close` DECIMAL,
	`high` DECIMAL NOT NULL,
	`low` DECIMAL NOT NULL,
	`volume` INT NOT NULL
);

CREATE TABLE IF NOT EXISTS history (
    `date` datetime NOT NULL,
    `symbol` CHAR NOT NULL,
    `open` DECIMAL NOT NULL,
    `close` DECIMAL NOT NULL,
    `adj_close` DECIMAL,
    `high` DECIMAL NOT NULL,
    `low` DECIMAL NOT NULL,
    `volume` INT NOT NULL,
    PRIMARY KEY (`date`, `symbol`)
);