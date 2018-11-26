select description, 
		sum(TotalSales) as Sales
from product_year_month_2015
group by description
order by sales desc
limit 1000

