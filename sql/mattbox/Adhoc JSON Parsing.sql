DELIMITER ;

use w3hacknet;
delimiter $$$
set @json_doc = '{
      "json": {
        "inserts": 1,
        "deletes": 1,
        "occurrences": 1
      },
      "html": {
        "inserts": 1,
        "deletes": 1,
        "occurrences": 1
      },
      "js": {
        "inserts": 235,
        "deletes": 100,
        "occurrences": 3
      }
	}';

select json_value(json_query(@json_doc, '$.js'), '$.inserts');
set @key_idx = 0;
set @keys = json_keys(@json_doc);
while @key_idx < json_length(@keys) do
	select json_value(@keys, concat('$[',@key_idx,']')) into @key;
	select json_query(@json_doc, concat('$.',@key)) into @val;
	select json_value(@val, '$.inserts') into @inserts;
	select json_value(@val, '$.deletes') into @deletes;
	select json_value(@val, '$.occurrences') into @occurrences;
	select @key, @val, @inserts, @deletes, @occurrences;
	set @key_idx = @key_idx + 1;
end WHILE;

select json_keys(@json_doc);
SELECT @mkey = JSON_VALUE(JSON_KEYS(@json_doc), CONCAT('$[', seq, ']')), @mkey
	FROM seq_0_to_100000000 WHERE seq < JSON_LENGTH(JSON_KEYS(@json_doc));		
$$$
delimiter ;


use w3hacknet
set @json = '  {
    "commit": "90a1594adaa1bb121c6d7e96dbb0c061704b6ef5",
    "Author": "Olivier Biot <olivier.biot@me.com>",
    "Date": "2015-07-13T22:20:46-07:00",
    "orig_timezone": "UTC+08:00",
    "fileTypes": {
      "json": {
        "inserts": 1,
        "deletes": 1,
        "occurrences": 1
      },
      "html": {
        "inserts": 1,
        "deletes": 1,
        "occurrences": 1
      },
      "js": {
        "inserts": 235,
        "deletes": 100,
        "occurrences": 3
      }
    }
  }';
  
select json_value(@json, '$.commit') into @commit_id;
select json_value(@json, '$.Author') into @alias
select md5(@alias) into @author_hash;
select STR_TO_DATE(json_value(@json, '$.Date'), '%Y-%m-%dT%H:%i:%S') into @date;
select json_value(@json, '$.orig_timezone') into @orig_tz;
select json_query(@json, '$.fileTypes') into @file_types;
select 'owner_a', 'repo_b', @commit_id, @author_hash, @alias, @date, @orig_tz, @file_types;
call InsertCommit('owner_a', 'repo_b', @commit_id, @author_hash, @alias, @date, @orig_tz, @file_types)
select @commit_id
{ CALL w3hacknet.InsertCommit('owner_a', 'repo_b', @commit_id, @author_hash, @alias, @date, @orig_tz, @file_types) }

select * from repo order by id desc

	select * from repo_commit where repo_id = 23 order by id desc
select commit_id, repo_id, count(*) from repo_commit group by commit_id, repo_id
order by 3 DESC 

SELECT id, commit_id, alias_id, `date`, gmt_offset
FROM w3hacknet.`commit`;
select * from commit_stats
select * from repo
select * FROM repo_commit
select count(*) from commit_stats
select count(*) from commit;
select * from commit_stats order by id desc
delete w3hacknet.commit where id = 8
