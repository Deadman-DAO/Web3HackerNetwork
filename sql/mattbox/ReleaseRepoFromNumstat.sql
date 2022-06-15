CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ReleaseRepoFromNumstat`(	
in _repo_id int,
in _numstat_machine_name varchar(64),
in _numstat_dir varchar(512),
in _repo_min_date datetime,
in _repo_max_date datetime,
in _repo_commit_count int
)
BEGIN
	declare dt datetime default current_timestamp(4);

	update repo set last_numstat_date = dt, 
		numstat_machine_name = _numstat_machine_name, 
		numstat_dir = _numstat_dir,
		commit_count = _repo_commit_count,
		min_date = _repo_min_date,
		max_date = _repo_max_date,
		last_analysis_date = null
	 where id = _repo_id;
	update repo_reserve set tstamp = dt where repo_id = _repo_id;	
END