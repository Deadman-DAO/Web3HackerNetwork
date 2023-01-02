DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ReleaseRepoAfterCleanup_v01` (
IN _repo_id int(11),
IN _machine_name varchar(64)
)
BEGIN
	update repo 
	   set 	repo_machine_name = null, 
	   		repo_dir = null, 
   			numstat_machine_name = null, 
   			numstat_dir = null,
   			last_machine = _machine_name
	 where id = _repo_id;
	delete from repo_reserve where repo_id = _repo_id;	
	
END
/MANGINA/
DELIMITER ;
