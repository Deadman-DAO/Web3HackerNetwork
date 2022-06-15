CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ReserveRepoForNumstat`(
in machine_name varchar(64)
)
BEGIN
	declare dt datetime default now();
	declare last_id int;

	select r.id, r.owner, r.name, r.repo_dir from repo r
	join repo_reserve rr on rr.repo_id = r.id 
	where rr.reserver = machine_name
	  and r.repo_machine_name = machine_name 
	  and r.repo_dir is not NULL
	  and r.numstat_machine_name is NULL 
	  and r.numstat_dir is null
	  and r.failed_date is null
	  limit 1;
		  	
END