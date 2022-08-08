DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`PostProcessHackerUpdate` (
IN max_records int(11)
)
BEGIN
	declare _id int;
	declare	_md5 char(32);
	declare _nemail varchar(256);
	declare _commit_count int;
	declare _min_date datetime;
	declare _max_date datetime;
	declare _repo_owner varchar(128);
	declare _repo_name varchar(128);
	declare _commit_array json;
	declare _counter int default 0;


	drop temporary table if exists delq;
	create temporary table delq (delq_id int);
	create index WTFWTF2 on delq(delq_id);
	drop temporary table if exists markq;
	create temporary table markq (markq_id int);
	create index WTFWTF3 on markq(markq_id);

	insert into markq (markq_id) select id from hacker_update_queue huq 
  		order by id limit max_records;

	while exists (select * from markq) DO
		
		select id, md5, name_email, commit_count, min_date, max_date, commit_array, repo_owner, repo_name into 
			_id, _md5, _nemail, _commit_count, _min_date, _max_date, _commit_array, _repo_owner, _repo_name
		  from hacker_update_queue huq2 
		  join markq q on q.markq_id = huq2.id
		  order by markq_id asc
		  limit 1;
		call UpdateHacker(_md5, _nemail, _commit_count, _min_date, _max_date, _repo_owner, _repo_name, _commit_array);
		insert into delq (delq_id) values (_id);
		delete from markq where markq_id = _id;
		set _counter = _counter + 1; 
	end while;

#	update hacker_update_queue set deleteme = 1 where id in (select delq_id from delq);

	drop temporary table if exists delq;
	drop temporary table if exists markq;

	select _counter;
END
/MANGINA/
DELIMITER ;
