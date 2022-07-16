DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ReserveNextRepo` (
IN _who_is_reserving varchar(64),
OUT _repo_owner varchar(128),
OUT _repo_name varchar(128),
OUT _repo_id int(11)
)
BEGIN
	declare exit handler for SQLEXCEPTION
	begin
        GET DIAGNOSTICS CONDITION 1 @p1 = RETURNED_SQLSTATE, @p2 = MESSAGE_TEXT;
		call debug(CONCAT('Exception occurred in ReserveNextRepo ',@p1, ':', @p2));
		delete from rediculous_fucking_work_around where connection_id = connection_id();
	end;
	select -1, null, null into _repo_id, _repo_owner, _repo_name;

	call FillRepoJobQueueIfNecessary();
	delete from staged_repo_job_q 
		order by id
		limit 1;
	select repo_id into _repo_id from rediculous_fucking_work_around where connection_id = connection_id();
	delete from rediculous_fucking_work_around where connection_id = connection_id();
	
	if _repo_id > 0 then
		insert into repo_reserve (repo_id, tstamp, reserver) values (_repo_id, now(3), _who_is_reserving);
		select owner, name into _repo_owner, _repo_name from repo where id = _repo_id;
	end if; 

END
/MANGINA/
DELIMITER ;
