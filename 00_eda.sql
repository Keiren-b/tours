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
    C AS tour_type,
    D AS guide,
    CASE lower(trim(E))
        WHEN 'yes' THEN TRUE
        WHEN 'no'  THEN FALSE
    END AS needed,
    TRY_CAST(F AS DOUBLE) AS headcount_per_group
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
    J AS tour_type,
    K AS guide,
    CASE lower(trim(L))
        WHEN 'yes' THEN TRUE
        WHEN 'no'  THEN FALSE
    END AS needed,
    TRY_CAST(M AS DOUBLE) AS headcount_per_group
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
-- Columns now include a start and end headcount figure. End likely to be dropped in analysis. End likely to be dropped in analysis. End (col U now dropped as redundant)

CREATE OR REPLACE TABLE year_2020 AS
SELECT
    DATE '1899-12-30' + TRY_CAST(P AS INTEGER) AS tour_date,
    Q AS tour_type,
    R AS guide,
    CASE lower(trim(S))
        WHEN 'yes' THEN TRUE
        WHEN 'no'  THEN FALSE
    END AS needed,
    TRY_CAST(T AS DOUBLE) AS headcount_per_group,
    --TRY_CAST(U AS INTEGER) AS headcount_per_group_end
FROM read_xlsx(
    'data/raw/numbers_raw.xlsx',
    header      = false,
    sheet       = 'SS Info dump',
    --range       = 'P3:U',
    range       = 'P3:T',

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
-- Column Z (Needed) now has 2 rows where there are values for No Tour and Scheduled? 
-- Handle No Tour as 0 since is it Xmas day and we will make a flag for that, cast scheduled as True 

--SELECT *
--FROM read_xlsx(
--    'data/raw/numbers_raw.xlsx',
--    header      = false,
 --   sheet       = 'SS Info dump',
 --   range       = 'W3:AD',
 --   all_varchar = true
--)
--WHERE W IS NOT NULL
--AND (lower(Z) NOT IN ('yes', 'no'));


CREATE OR REPLACE TABLE year_2022 AS
SELECT
    DATE '1899-12-30' + TRY_CAST(W AS INTEGER) AS tour_date,
    X AS tour_type,
    Y AS guide,
    CASE
        WHEN lower(trim(Z)) IN ('yes', 'scheduled?') THEN TRUE
        WHEN lower(trim(Z)) IN ('no', 'no tour') THEN FALSE
    END AS needed,
    COALESCE(TRY_CAST(AA AS DOUBLE), 0) + COALESCE(TRY_CAST(AB AS DOUBLE), 0) * 0.5 AS headcount_per_group   
    --TRY_CAST(AB AS INTEGER) AS headcount_per_group_start_child,
    --TRY_CAST(AC AS INTEGER) AS headcount_per_group_end_adult,
    --TRY_CAST(AD AS INTEGER) AS headcount_per_group_end_child,


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
-- Columns now include a start and end headcount figure. End likely to be dropped in analysis.
-- Counts also split into adults and kids. Kids need to be handled, perhaps count as 0.5

CREATE OR REPLACE TABLE year_2023 AS
SELECT
    DATE '1899-12-30' + TRY_CAST(AF AS INTEGER) AS tour_date,
    AG AS tour_type,
    AH AS guide,
    CASE lower(trim(AI))
        WHEN 'yes' THEN TRUE
        WHEN 'no'  THEN FALSE
    END AS needed,
    COALESCE(TRY_CAST(AJ AS DOUBLE), 0) + COALESCE(TRY_CAST(AK AS DOUBLE), 0) * 0.5 AS headcount_per_group
    --TRY_CAST(AJ AS INTEGER) AS headcount_per_group_start_adult,
    --TRY_CAST(AK AS INTEGER) AS headcount_per_group_start_child,
    --TRY_CAST(AL AS INTEGER) AS headcount_per_group_end_adult,
    --TRY_CAST(AM AS INTEGER) AS headcount_per_group_end_child,
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
UNION ALL BY NAME
SELECT * FROM year_2019
UNION ALL BY NAME
SELECT * FROM year_2020
UNION ALL BY NAME
SELECT * FROM year_2022
UNION ALL BY NAME
SELECT * FROM year_2023;

SELECT * 
FROM all_years;

SELECT tour_date, SUM(headcount_per_group)
FROM all_years
GROUP BY tour_date;

SELECT DISTINCT tour_type
FROM all_years;

SELECT count(*) FROM all_years WHERE needed IS NOT TRUE;
-----------------------------------------------------
-- multiple tours run per day, need to separate out
-- values for NO TOUR need to be dropped
-- For initial training just do morning tours, drop afternoon
-- remove rows where guide not needed
-- calculate number of guides needed
-- add year and month for later analysis
CREATE OR REPLACE TABLE all_years_morning AS
SELECT
tour_date,
YEAR(tour_date) AS tour_year,
MONTH(tour_date) as tour_month,
count(*) AS num_guides,
SUM(headcount_per_group) AS headcount,
FROM all_years
WHERE tour_type = 'Sydney Sights 10:30am' AND needed IS TRUE
GROUP BY tour_date;

SELECT * 
FROM all_years_morning;

-- COPY all_years_morning TO 'data/cleaned/morning.csv' (HEADER, DELIMITER ',');
CREATE or REPLACE TABLE weather_hourly AS
SELECT * FROM read_xlsx(
    'data/raw/weather_hourly.xlsx', 
header = false, 
all_varchar = true);

SELECT * FROM 
read_xlsx(
    'data/raw/weather_daily.xlsx', 
header = false, 
all_varchar = true);


-- fit a seasonal naive first: predict each day as the same weekday last week. 
-- It takes two lines and it's a shockingly strong baseline on daily operational data. 
--Every subsequent model gets judged against it
