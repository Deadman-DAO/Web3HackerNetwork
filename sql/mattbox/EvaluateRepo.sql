DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`EvaluateRepo` (
IN _repo_owner varchar(128),
IN _repo_name varchar(128),
IN _created_at datetime,
IN _updated_at datetime,
IN _pushed_at datetime,
IN _homepage varchar(256),
IN _size int(11),
IN _watchers int(11),
IN _commit_count_last_year int(11)
)
BEGIN
	declare _repo_id int default -1;
	declare _dupe_repo_count int default -1;
	declare _dupe_repo_commit_count int default -1;

	select id into _repo_id from repo r where r.owner  = _repo_owner and r.name = _repo_name;
	if _repo_id > 0 then
		select count(rep), sum(cnt) into _dupe_repo_count, _dupe_repo_commit_count from (
		select outer_rc.repo_id as rep, count(*) as cnt from repo_commit outer_rc
		where outer_rc.commit_id in (
			select commit_id from repo_commit rc 
			where rc.repo_id = _repo_id)
		and outer_rc.repo_id != _repo_id
		group by outer_rc.repo_id
		) as X;
		
		insert ignore into repo_eval (repo_id, created_at, updated_at, pushed_at, homepage, size, watchers, commit_count_last_year, parallel_repo_count)
		  values (_repo_id, _created_at, _updated_at, _pushed_at, _homepage, _size, _watchers, _commit_count_last_year, _dupe_repo_count);
		delete from repo_reserve where repo_id = _repo_id;
	end if;

END
/MANGINA/
DELIMITER ;
