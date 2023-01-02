DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`GetNextRepoForEval` (
IN _machine_name varchar(64),
OUT _owner varchar(128),
OUT _name varchar(128),
OUT _repo_id int(11)
)
BEGIN
	declare exit handler for SQLEXCEPTION
	begin
        GET DIAGNOSTICS CONDITION 1 @p1 = RETURNED_SQLSTATE, @p2 = MESSAGE_TEXT;
		call debug(CONCAT('Exception in GetNextRepoForEval ',@p1, ':', @p2, ' machine: ', _machine_name));
	end;
	
	select X.repo_id, X.owner, X.name into _repo_id, _owner, _name 
	  From repos_staged_for_eval X
	  left join repos_staged_for_eval_reserve res on res.repo_id = X.repo_id
  	  where randy > rand() and res.repo_id is null
      order by randy, X.repo_id	
	  limit 1;
	 
	if _repo_id is not null then
		insert into repos_staged_for_eval_reserve (repo_id, machine) values (_repo_id, _machine_name);
	end if;
	
END
/MANGINA/
DELIMITER ;
