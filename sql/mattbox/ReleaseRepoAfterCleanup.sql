DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ReleaseRepoAfterCleanup` (
IN _repo_id int(11)
)
BEGIN
	update repo 
	   set 	repo_machine_name = null, 
	   		repo_dir = null, 
   			numstat_machine_name = null, 
   			numstat_dir = null
	 where id = _repo_id;
	delete from repo_reserve where repo_id = _repo_id;	
	
END
/MANGINA/
DELIMITER ;
