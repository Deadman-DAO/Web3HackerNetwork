DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ReserveNextRepoForCleanup` (
IN _machine_name varchar(64)
)
BEGIN
	declare _dt datetime default now();
	declare _last_id int;
	declare _repo_id int;

	select r.id, r.owner, r.name, r.repo_dir from repo r
		join repo_reserve rr on rr.repo_id = r.id 
		where rr.reserver = _machine_name
		  and r.repo_machine_name = _machine_name
		  and r.numstat_machine_name = _machine_name  
 		  and r.last_analysis_date is not null
	limit 1;
END
/MANGINA/
DELIMITER ;
