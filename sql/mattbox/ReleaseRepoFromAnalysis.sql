CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ReleaseRepoFromAnalysis`(
	in _repo_id int,
	in _numstat longblob,
	in _success bit
)
BEGIN
	declare dt datetime default now();
	update repo set last_analysis_date = dt, failed_date = case when _success then null else dt end
	 where id = _repo_id;
	update repo_reserve set tstamp = dt where repo_id = _repo_id;	
	insert into repo_numstat (repo_id, tstamp, numstat) values (_repo_id, dt, _numstat);

END