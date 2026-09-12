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
    TRY_CAST(F AS DOUBLE) AS headcount_per_group,
    'SS dump' AS source
FROM read_xlsx(
    'data/raw/numbers_raw.xlsx',
    header      = false,
    sheet       = 'SS Info dump',
    range       = 'B3:F',
    all_varchar = true
)
WHERE B IS NOT NULL;


SELECT * FROM year_2018;
SELECT MIN(tour_date) from year_2018;

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
    TRY_CAST(M AS DOUBLE) AS headcount_per_group,
    'SS dump' AS source

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
    'SS dump' AS source

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
    COALESCE(TRY_CAST(AA AS DOUBLE), 0) + COALESCE(TRY_CAST(AB AS DOUBLE), 0) * 0.5 AS headcount_per_group,
    'SS dump' AS source   
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
-- Dates only go to 31 Oct in this table. 
-- Will join with another table that lists all dates to Aug 2026 at end of this process

CREATE OR REPLACE TABLE year_2023 AS
SELECT
    DATE '1899-12-30' + TRY_CAST(AF AS INTEGER) AS tour_date,
    AG AS tour_type,
    AH AS guide,
    CASE lower(trim(AI))
        WHEN 'yes' THEN TRUE
        WHEN 'no'  THEN FALSE
    END AS needed,
    COALESCE(TRY_CAST(AJ AS DOUBLE), 0) + COALESCE(TRY_CAST(AK AS DOUBLE), 0) * 0.5 AS headcount_per_group,
    'SS dump' AS source
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

-------------------------------------------------
-- pull data from source listing tours to aug 26
-------------------------------------------------

SELECT * 
FROM read_xlsx('data/raw/all_bookings_raw_22on.xlsx',
header = true,
all_varchar = true);

SELECT DISTINCT
"Valid For Time"
FROM read_xlsx('data/raw/all_bookings_raw_22on.xlsx',
header = true,
all_varchar = true);

CREATE OR REPLACE TABLE raw_22on AS
WITH src AS (
    SELECT
        DATE '1899-12-30' + TRY_CAST("Valid For Date" AS INTEGER) AS tour_date,
        TRY_CAST("Tier 1 Size" AS INTEGER) AS tier1,
        TRY_CAST("Tier 2 Size" AS INTEGER) AS tier2
    FROM read_xlsx('data/raw/all_bookings_raw_22on.xlsx', header = true, all_varchar = true)
    WHERE Product = 'Sydney Sights'
          AND ROUND(TRY_CAST("Valid For Time" AS DOUBLE) * 1440) = 630
)
SELECT
    tour_date,
    'Sydney Sights 10:30am' AS tour_type,
    CAST(NULL AS VARCHAR)   AS guide,
    TRUE                    AS needed,
    SUM(tier1) + 0.5 * SUM(COALESCE(tier2, 0)) AS headcount_per_group,
    'all_bookings_raw'      AS source
FROM src
WHERE tour_date > (SELECT MAX(tour_date) FROM year_2023)
  AND tour_date <= DATE '2026-08-31'
GROUP BY ALL;

SELECT MAX(tour_date) FROM year_2023;
SELECT MIN(tour_date), MAX(tour_date), COUNT(*) FROM raw_22on;

SELECT * FROM raw_22on;
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
SELECT * FROM year_2023
UNION ALL BY NAME
SELECT * FROM raw_22on
ORDER BY tour_date;

--SELECT * FROM oct23_to_aug26
--WHERE tour_date > DATE '2023-10-31';

--LEFT JOIN oct23_to_aug26 on all_years.tour_date = oct23_to_aug26.tour_date;

--FROM date_spine s
--LEFT JOIN all_years_morning m ON m.tour_date = s.date_day
--ORDER BY s.date_day;
SELECT * from all_years;


SELECT * 
FROM all_years_ss_dump;

SELECT tour_date, SUM(headcount_per_group)
FROM all_years_ss_dump
WHERE tour_type = 'Sydney Sights 10:30am'
GROUP BY tour_date;


SELECT DISTINCT tour_type
FROM all_years_ss_dump;

SELECT count(*) FROM all_years_ss_dump WHERE needed IS NOT TRUE;
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
source
FROM all_years
WHERE tour_type = 'Sydney Sights 10:30am' AND needed IS TRUE
GROUP BY tour_date, source;

CREATE OR REPLACE TABLE date_spine AS
SELECT r.ts::DATE AS date_day
FROM (SELECT MIN(tour_date) AS lo, MAX(tour_date) AS hi FROM all_years_morning) b,
     range(b.lo, b.hi + INTERVAL 1 DAY, INTERVAL 1 DAY) r(ts);

CREATE OR REPLACE TABLE vivid AS
SELECT * FROM (VALUES
    (2018, DATE '2018-05-25', DATE '2018-06-16'),
    (2019, DATE '2019-05-24', DATE '2019-06-15'),
    -- 2020 and 2021 cancelled: deliberately absent
    (2022, DATE '2022-05-27', DATE '2022-06-18'),
    (2023, DATE '2023-05-26', DATE '2023-06-17'),
    (2024, DATE '2024-05-24', DATE '2024-06-15'),
    (2025, DATE '2025-05-23', DATE '2025-06-14'),
    (2026, DATE '2026-05-22', DATE '2026-06-13'),
    (2027, DATE '2027-05-28', DATE '2027-06-19')
) AS t(vivid_year, vivid_start, vivid_end);

CREATE OR REPLACE TABLE all_years_morning AS
SELECT
    s.date_day                  AS tour_date,
    YEAR(s.date_day)            AS tour_year,
    MONTH(s.date_day)           AS tour_month,
    DAY(s.date_day)             as tour_day,
    DAYNAME(s.date_day)         AS day_name,
    DAYOFWEEK(s.date_day)       AS day_of_week,
    COALESCE(m.num_guides, 0)   AS num_guides,
    COALESCE(m.headcount, 0)    AS headcount,
    s.date_day BETWEEN DATE '2020-03-23' AND DATE '2021-12-31' AS covid_flag,
    MONTH(s.date_day) = 12 AND DAY(s.date_day) = 25 AS xmas_flag,
    COALESCE(m.source, 'date spine')                AS source
FROM date_spine s
LEFT JOIN all_years_morning m ON m.tour_date = s.date_day
ORDER BY s.date_day;

SELECT * FROM all_years_morning WHERE tour_date = DATE('2023-04-20');
SELECT * FROM all_years_morning;

COPY all_years_morning TO 'data/processed/morning.csv' (HEADER, DELIMITER ',');

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

SELECT MAX(tour_date) AS latest_date FROM all_years_morning;

-- fit a seasonal naive first: predict each day as the same weekday last week. 
-- It takes two lines and it's a shockingly strong baseline on daily operational data. 
--Every subsequent model gets judged against it

SELECT * FROM all_years_morning;

CREATE OR REPLACE TABLE o_2022 AS
SELECT
    DATE '1899-12-30' + TRY_CAST(W AS INTEGER) AS tour_date,
    X AS tour_type,
    SUM(COALESCE(TRY_CAST(AA AS DOUBLE), 0) + COALESCE(TRY_CAST(AB AS DOUBLE), 0) * 0.5) AS headcount,
    'SS dump' AS source   
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
WHERE W IS NOT NULL and lower(trim(Z)) IN ('yes', 'scheduled?') and lower(trim(X)) = 'sydney sights 10:30am'
GROUP BY DATE '1899-12-30' + TRY_CAST(W AS INTEGER), X; 


SELECT * from o_2022;