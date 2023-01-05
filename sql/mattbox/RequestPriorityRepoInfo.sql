DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`RequestPriorityRepoInfo` (
IN _repo_owner varchar(128),
IN _repo_name varchar(128)
)
BEGIN
	declare _repo_id int default null;
	select id into _repo_id from repo where owner = _repo_owner and name = _repo_name;
	if _repo_id is not null then
		insert into priority_repos_staged_for_eval (repo_id) select _repo_id;
	end if;
END
/MANGINA/
DELIMITER ;
