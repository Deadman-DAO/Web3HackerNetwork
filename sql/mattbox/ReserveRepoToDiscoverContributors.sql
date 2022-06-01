CREATE PROCEDURE w3hacknet.ReserveRepoToDiscoverContributors(
	in _reserver_user_id varchar(32)
)
BEGIN
	declare _owner varchar(128);
	declare _name varchar(128);
	declare _repo_id int;
	declare success bit;

	select id, owner, name from repo r
		left join repo_reserve rr on rr.repo_id = r.id 
		join repo_eval re on re.repo_id = r.id 
		where rr.repo_id is null and re.repo_id  is not null and re.contributor_count is NULL 
		limit 1;
	
	call reserveRepo(_owner, _name, _reserver_user_id, success);
	if success = 1 then
		select _repo_id, _owner, _name;
	end if;
	

END