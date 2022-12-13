DELIMITER /MANGINA/
create or replace trigger
 
clear_me_insert
BEFORE
INSERT
 on 
clear_me
 for each row 
BEGIN 
	update repo set repo_machine_name = null, repo_dir = null, numstat_machine_name = null, numstat_dir = null, last_cloned_date = null, last_numstat_date = null, last_analysis_date = null 
	  where name = new.repo_name and owner = new.repo_owner;
END
/MANGINA/
DELIMITER ;
