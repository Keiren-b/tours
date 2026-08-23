SELECT * FROM read_xlsx(
    'data/raw/numbers_raw.xlsx', 
header = false, 
sheet = 'SS Info dump',
range = 'A1:ZZ100', 
all_varchar = true);

-- Column A is blank
-- Data is scattered across in long format, with years spread out as 4 columns
-- Column headers are inconsistently named
-- 2018: Multiple rows per day, 2 different tours a day, multiple guides with a binary yes/no if they're needed. Number of people per guide not total


-------------------
-- 2018 Cleaning
-------------------

CREATE OR REPLACE TABLE year_2018 AS
SELECT
    DATE '1899-12-30' + TRY_CAST(B AS INTEGER) AS tour_date,
    CAST(C AS TEXT) AS tour_type,
    CAST(D AS TEXT) AS guide,
    CASE lower(trim(E))
        WHEN 'yes' THEN TRUE
        WHEN 'no'  THEN FALSE
    END AS needed,
    TRY_CAST(F AS INTEGER) AS headcount_per_group
FROM read_xlsx(
    'data/raw/numbers_raw.xlsx',
    header      = false,
    sheet       = 'SS Info dump',
    range       = 'B3:F',
    all_varchar = true
)
WHERE B IS NOT NULL;


SELECT * FROM year_2018
-- Any rows that failed to convert?
--SELECT count(*) AS total, count(tour_date) AS parsed FROM year_2018;

-- Do the dates fall in the year you expect?
--SELECT min(tour_date), max(tour_date) FROM year_2018;




--CREATE or REPLACE TABLE year_2019 AS
--SELECT * FROM read_xlsx(
--    'data/raw/numbers_raw.xlsx', 
--header = false, 
--sheet = 'SS Info dump',
--range = 'I3:N', 
--all_varchar = true);


