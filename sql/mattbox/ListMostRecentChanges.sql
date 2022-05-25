
select table_schema as database_name,
       table_name,
       update_time
from information_schema.tables tab
where update_time > (current_timestamp() - interval 30 day)
      and table_type = 'BASE TABLE'
      and table_schema not in ('information_schema', 'sys',
                               'performance_schema','mysql')
      -- and table_schema = 'your database name' 
order by update_time desc;