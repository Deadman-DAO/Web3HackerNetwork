DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ReleaseRepoFromAnalysis` (
IN _repo_id int(11),
IN _numstat longblob,
IN _success bit(1)
)
BEGIN
	declare dt datetime default now();
	update repo set last_analysis_date = dt, failed_date = case when _success then null else dt end
	 where id = _repo_id;
	update repo_reserve set tstamp = dt where repo_id = _repo_id;	
	insert into repo_numstat (repo_id, tstamp, numstat) values (_repo_id, dt, _numstat)
		on DUPLICATE key update tstamp = dt, numstat = _numstat;

END
/MANGINA/
DELIMITER ;
