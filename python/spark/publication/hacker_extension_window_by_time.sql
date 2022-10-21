select author, extension,
  year, quarter, month,
  year as year_ce, quarter + 4 * year as quarter_ce, month + 12 * year as month_ce,
  sum(num_files) over(partition by author, extension, year order by year) as year_files,
  sum(num_files) over(partition by author, extension, year, quarter order by year, quarter) as qrtr_files,
  num_files as month_files,
  sum(lines_added) over(partition by author, extension, year order by year) as year_lines,
  sum(lines_added) over(partition by author, extension, year, quarter order by year, quarter) as qrtr_lines,
  lines_added as month_lines
from (
  select author,
       extension,
       date_format(year_month, '%Y-%m') as YYYYmm,
       total_inserts as lines_added,
       num_files,
       year(year_month) as year,
       cast(truncate((month(year_month) + 2) / 3.0) as integer) as quarter,
       month(year_month) as month
  from curated_hacker_extension_monthly
  where author = 'Guido van Rossum <guido@python.org>'
) foo
order by year, extension, YYYYmm asc
