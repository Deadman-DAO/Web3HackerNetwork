CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ReserveNextRepoForAnalysis`(
in _machine_name varchar(64))
BEGIN
	declare _dt datetime default now();
	declare _last_id int;
	declare _repo_id int default -1;

	select r.id, r.owner, r.name, r.repo_dir, r.numstat_dir  from repo r
		join repo_reserve rr on rr.repo_id = r.id 
		where rr.reserver = _machine_name
		  and r.repo_machine_name = _machine_name 
		  and r.numstat_machine_name = _machine_name 
 		  and r.last_analysis_date is null
	  limit 1;

END