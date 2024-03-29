DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`SetRepoWatcherCount` (
IN _repo_owner varchar(128),
IN _repo_name varchar(128),
IN _num_watchers int(11),
IN _size int(11),
IN _subscribers int(11)
)
BEGIN
	declare _nowish datetime default(now(3));
	declare _repo_id int default null;

#	call debug(concat('SetRepoWatchCount:', _nowish, ' Entry'));
	insert into repo_eval_queue (owner, name, watchers, repo_size, subscribers, inserted_at) values 
      (_repo_owner, _repo_name, _num_watchers, _size, _subscribers, _nowish);
#    select now(3) into _nowish;
#	call debug(concat('SetRepoWatchCount:', _nowish, ' repo_eval_queue inserted'));
    
	select repo_id into _repo_id from 
		repos_staged_for_eval e
		where e.owner = _repo_owner and e.name = _repo_name;
#    select now(3) into _nowish;
#	call debug(concat('SetRepoWatchCount:', _nowish, ' repo_id looked up from repo_staged_for_eval table'));
	
	if _repo_id is not null then
		delete from priority_repos_staged_for_eval where repo_id = _repo_id;
		delete from repos_staged_for_eval where repo_id = _repo_id;
		delete from repos_staged_for_eval_reserve where repo_id = _repo_id;
	end if;
#    select now(3) into _nowish;
#	call debug(concat('SetRepoWatchCount:', _nowish, ' cleaned up staged, priority-staged and reserve'));
	
END
/MANGINA/
DELIMITER ;
