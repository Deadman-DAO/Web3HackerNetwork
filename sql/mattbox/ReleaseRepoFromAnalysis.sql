CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ReleaseRepoFromAnalysis`(
	in _repo_id int
)
BEGIN
	declare dt datetime default now();
	update repo set last_analysis_date = dt
	 where id = _repo_id;
	update repo_reserve set tstamp = dt where repo_id = _repo_id;	

END