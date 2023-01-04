DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ReleaseRepoFromCloning` (
IN _repo_id int(11),
IN _machine_name varchar(64),
IN _repo_dir varchar(512),
IN _success bit(1)
)
BEGIN
	declare dt datetime default now();
    /* The Cleanup process is looking for repo records matching:
    		where rr.reserver = _machine_name
		  and r.repo_machine_name = _machine_name
		  and r.numstat_machine_name = _machine_name  
 		  and r.last_analysis_date is not null
       So if this has errored out (_success = 0) then we should make sure the repo record is left in this state */
	update repo set repo_machine_name = _machine_name, 
		repo_dir = _repo_dir, 
		last_cloned_date = dt,
		last_numstat_date = case when _success then null else dt end ,
		last_analysis_date = case when _success then null else dt end ,
		numstat_dir = case when _success then null else _repo_dir end ,
		numstat_machine_name = case when _success then null else _machine_name end ,
        repo_machine_name = case when _success then null else _machine_name end ,
		failed_date = case when _success then null else dt end 
	 where id = _repo_id;
	update repo_reserve set tstamp = dt where repo_id = _repo_id;
END
/MANGINA/
DELIMITER ;
