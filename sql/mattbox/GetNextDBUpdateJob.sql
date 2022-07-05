DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`GetNextDBUpdateJob` (
IN _machine_name varchar(64)
)
BEGIN
	declare ts datetime default now();
	declare job_id int default -1;
	insert into db_update_archive (db_update_queue_id, reserved)
		select duq.id, ts from db_update_queue duq
			left join db_update_archive a on a.db_update_queue_id = duq.id 
			where a.db_update_queue_id is null and machine_name = _machine_name
			order by duq.tstamp 
			limit 1;
	if row_count() > 0 then
		select LAST_INSERT_ID() into job_id;
		select repo_owner, repo_name from db_update_queue where id = job_id;
	end if;
		
END
/MANGINA/
DELIMITER ;
