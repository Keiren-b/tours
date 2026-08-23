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


SELECT * FROM year_2018;

-------------------
-- 2019 Cleaning
------------------
-- Columns now include a start and end headcount figure. End likely to be dropped in analysis. End (col N now dropped as redundant)

CREATE OR REPLACE TABLE year_2019 AS
SELECT
    DATE '1899-12-30' + TRY_CAST(I AS INTEGER) AS tour_date,
    CAST(J AS TEXT) AS tour_type,
    CAST(K AS TEXT) AS guide,
    CASE lower(trim(L))
        WHEN 'yes' THEN TRUE
        WHEN 'no'  THEN FALSE
    END AS needed,
    TRY_CAST(M AS INTEGER) AS headcount_per_group
    --TRY_CAST(N AS INTEGER) AS headcount_per_group_end
FROM read_xlsx(
    'data/raw/numbers_raw.xlsx',
    header      = false,
    sheet       = 'SS Info dump',
    range = 'I3:M',
    --range       = 'I3:N',
    all_varchar = true
)
WHERE I IS NOT NULL;

SELECT * from year_2019;


-------------------
-- 2020 Cleaning
------------------
-- Columns now include a start and end headcount figure. End likely to be dropped in analysis

CREATE OR REPLACE TABLE year_2020 AS
SELECT
    DATE '1899-12-30' + TRY_CAST(P AS INTEGER) AS tour_date,
    CAST(Q AS TEXT) AS tour_type,
    CAST(R AS TEXT) AS guide,
    CASE lower(trim(S))
        WHEN 'yes' THEN TRUE
        WHEN 'no'  THEN FALSE
    END AS needed,
    TRY_CAST(T AS INTEGER) AS headcount_per_group_start,
    TRY_CAST(U AS INTEGER) AS headcount_per_group_end
FROM read_xlsx(
    'data/raw/numbers_raw.xlsx',
    header      = false,
    sheet       = 'SS Info dump',
    range       = 'P3:U',
    all_varchar = true
)
WHERE P IS NOT NULL;

SELECT * from year_2020;

---------------------------------------------------------
-- 2021 Cleaning: Data not available because of COVID
---------------------------------------------------------

-------------------
-- 2022 Cleaning
------------------
-- Columns now include a start and end headcount figure. End likely to be dropped in analysis.
-- Counts also split into adults and kids. Kids need to be handled, perhaps count as 0.5

CREATE OR REPLACE TABLE year_2022 AS
SELECT
    DATE '1899-12-30' + TRY_CAST(W AS INTEGER) AS tour_date,
    CAST(X AS TEXT) AS tour_type,
    CAST(Y AS TEXT) AS guide,
    CASE lower(trim(Z))
        WHEN 'yes' THEN TRUE
        WHEN 'no'  THEN FALSE
    END AS needed,
    TRY_CAST(AA AS INTEGER) AS headcount_per_group_start_adult,
    TRY_CAST(AB AS INTEGER) AS headcount_per_group_start_child,
    TRY_CAST(AC AS INTEGER) AS headcount_per_group_end_adult,
    TRY_CAST(AD AS INTEGER) AS headcount_per_group_end_child,
FROM read_xlsx(
    'data/raw/numbers_raw.xlsx',
    header      = false,
    sheet       = 'SS Info dump',
    range       = 'W3:AD',
    all_varchar = true
)
WHERE W IS NOT NULL;

SELECT * from year_2022;

-------------------
-- 2023 Cleaning
------------------
-- Columns now include a start and end headcount figure. End likely to be dropped in analysis

CREATE OR REPLACE TABLE year_2023 AS
SELECT
    DATE '1899-12-30' + TRY_CAST(AF AS INTEGER) AS tour_date,
    CAST(AG AS TEXT) AS tour_type,
    CAST(AH AS TEXT) AS guide,
    CASE lower(trim(AI))
        WHEN 'yes' THEN TRUE
        WHEN 'no'  THEN FALSE
    END AS needed,
    TRY_CAST(AJ AS INTEGER) AS headcount_per_group_start_adult,
    TRY_CAST(AK AS INTEGER) AS headcount_per_group_start_child,
    TRY_CAST(AL AS INTEGER) AS headcount_per_group_end_adult,
    TRY_CAST(AM AS INTEGER) AS headcount_per_group_end_child,
FROM read_xlsx(
    'data/raw/numbers_raw.xlsx',
    header      = false,
    sheet       = 'SS Info dump',
    range       = 'AF3:AM',
    all_varchar = true
)
WHERE AF IS NOT NULL;

SELECT * from year_2023;

--------------------------------------------
-- Join all years into long table
--------------------------------------------
CREATE OR REPLACE TABLE all_years AS
SELECT * FROM year_2018
UNION ALL
SELECT * FROM year_2019
UNION ALL
SELECT * FROM year_2020
--UNION ALL
--SELECT * FROM year_2022
--UNION ALL
--SELECT * FROM year_2023
--UNION ALL;
