DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ReleaseRepoFromNumstat` (
IN _repo_id int(11),
IN _numstat_machine_name varchar(64),
IN _numstat_dir varchar(512),
IN _repo_min_date datetime,
IN _repo_max_date datetime,
IN _repo_commit_count int(11),
IN _success bit(1)
)
BEGIN
	declare dt datetime default current_timestamp(4);

	update repo set last_numstat_date = dt, 
		numstat_machine_name = _numstat_machine_name, 
		numstat_dir = _numstat_dir,
		commit_count = _repo_commit_count,
		min_date = _repo_min_date,
		max_date = _repo_max_date,
		last_analysis_date = case when _success then null else dt end,
		failed_date = case when _success then null else dt end
	 	where id = _repo_id;
	update repo_reserve set tstamp = dt where repo_id = _repo_id;	
END
/MANGINA/
DELIMITER ;
