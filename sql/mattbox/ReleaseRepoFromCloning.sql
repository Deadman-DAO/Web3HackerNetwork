CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ReleaseRepoFromCloning`(
in _repo_id int,
in _machine_name varchar(64),
in _repo_dir varchar(512),
in _success bit
)
BEGIN
	declare dt datetime default now();
	update repo set repo_machine_name = _machine_name, 
		repo_dir = _repo_dir, 
		last_cloned_date = dt,
		last_numstat_date = case when _success then null else dt end ,
		last_analysis_date = case when _success then null else dt end ,
		numstat_dir = case when _success then null else _repo_dir end ,
		numstat_machine_name = case when _success then null else _machine_name end ,
		failed_date = case when _success then null else dt end 
	 where id = _repo_id;
	update repo_reserve set tstamp = dt where repo_id = _repo_id;
END