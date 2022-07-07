select count(*), sum(length(numstat)), 
cast(
	concat(
		year(tstamp), '-', 
		month(tstamp), '-', 
		day(tstamp), ' ', 
		hour(tstamp), ':00')
as datetime) as hour
from repo_numstat rn2
group by hour
order by 3 desc
limit 1440
