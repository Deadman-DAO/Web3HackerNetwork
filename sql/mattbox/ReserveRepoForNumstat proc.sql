CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ReserveRepoForNumstat`(
in machine_name varchar(64)
)
BEGIN
	declare dt datetime default now();
	declare last_id int;
	insert into repo_reserve (repo_id, tstamp, reserver)
		select r.id, dt, machine_name from repo r
		left join repo_reserve rr on rr.repo_id = r.id 
		where rr.repo_id  is null
		  and r.repo_machine_name = machine_name 
		  and r.repo_dir is not NULL
		  and r.numstat_machine_name is NULL 
		  and r.numstat_dir is null
		  limit 1;
		 
		 
	 select last_insert_id() into last_id;
	
	select r.id, r.owner, r.name, r.repo_dir from repo r
	   join repo_reserve rr on rr.repo_id = r.id 
  	   where rr.id = last_id;
  	
END