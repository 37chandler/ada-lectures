-- Build a table of Sales by Hour
SELECT Hour 
       ,sum(Spend) as Sales
FROM HourSales
GROUP BY Hour

-- Build a table of Sales by Hour by Year
SELECT  SUBSTR(Dates,1,4) as Year
        ,Hour 
       ,sum(Spend) as Sales
FROM HourSales
GROUP BY Year, Hour
ORDER BY Year, Hour



-- Build a table of Sales by Hour for 2015
SELECT  SUBSTR(Dates,1,4) as Year
        ,Hour 
       ,sum(Spend) as Sales
FROM HourSales
WHERE Year = "2015"
GROUP BY Year, Hour
ORDER BY Year, Hour


-- Build a table of owner sales by month
SELECT Month 
       ,sum(Spend) as Sales
FROM OwnerSales
GROUP BY Month



-- Build a table of owner sales by month for owners who spent between $5K and $10K

-- First build a temporary table with owner sales
CREATE TEMP TABLE 
    IF NOT EXISTS
    OwnerSumSales AS
    SELECT CardNum
       ,sum(Spend) as Spend
     FROM OwnerSales
     GROUP BY CardNum

-- Now use that to query
SELECT Month 
       ,sum(Spend) as Sales
FROM OwnerSales
WHERE CardNum in (
        SELECT CardNum 
        FROM OwnerSumSales
        WHERE 5000 < Spend < 10000)
GROUP BY Month

-- Build a list of the top 10 selling products at the Wedge
SELECT Description
       ,sum(Spend) as Spend
FROM ProdSales
GROUP BY Description
Order BY Spend DESC
LIMIT 10

-- Maybe better? 
SELECT LOWER(Description) as Description
       ,sum(Spend) as Spend
FROM ProdSales
GROUP BY Description
Order BY Spend DESC
LIMIT 10


-- Build a list of the top 10 selling products at the Wedge by Year 2015 and 2016
DROP TABLE IF EXISTS Top2015

CREATE TEMP TABLE 
    IF NOT EXISTS
    Top2015 AS
SELECT LOWER(Description) as Description
		,Year
       ,sum(Spend) as Spend2015
FROM ProdSales
WHERE Year = 2015
GROUP BY Description
Order BY Spend DESC
LIMIT 10

DROP TABLE IF EXISTS Top2016

CREATE TEMP TABLE 
    IF NOT EXISTS
    Top2016 AS
SELECT LOWER(Description) as Description
       ,Year
       ,sum(Spend) as Spend2016
FROM ProdSales
WHERE Year = 2016
GROUP BY Description
Order BY Spend DESC
LIMIT 10

SELECT LOWER(Description) as Description
		,Year
		,sum(Spend) as Spend
FROM ProdSales
WHERE (Year = 2015 or Year = 2016) and
	(LOWER(Description) in (select description from Top2016) or
	 LOWER(Description) in (select description from Top2015))
GROUP BY Description, Year
ORDER BY Spend

