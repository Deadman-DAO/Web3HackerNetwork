CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ReserveNextRepoForCleanup`(
in _machine_name varchar(64))
BEGIN
	declare _dt datetime default now();
	declare _last_id int;
	declare _repo_id int;

	insert into repo_reserve (repo_id, tstamp, reserver)
		select r.id, _dt, _machine_name 
		  from repo r
		left join repo_reserve rr on rr.repo_id = r.id 
		where rr.repo_id  is null
		  and r.repo_machine_name = _machine_name 
		  and r.repo_dir is not NULL
		  and r.numstat_machine_name = _machine_name 
		  and r.numstat_dir is not null
 		  and r.last_analysis_date is not null
	limit 1;
		 
    select last_insert_id() into _last_id;
	select r.id, r.owner, r.name, r.repo_dir from repo r
	   join repo_reserve rr on rr.repo_id = r.id 
  	   where rr.id = _last_id;
END