CREATE PROCEDURE w3hacknet.AddContributors(
in _repo_id int,
in _json json
)
BEGIN
	declare _len int default json_length(_json);
	declare _idx int default 0;
	declare _user_id varchar(256);
	declare _md5 char(32);
	declare _count int default 0;
	declare _contributor json;
	declare _alias_id int default -1;
	declare _sum int default 0;

	while _idx < _len DO
		set _contributor = json_query(_json, concat('$[', _idx, ']'));
		set _user_id = json_value(_contributor, '$.login');
		set _count = json_value(_contributor, '$.change_count');
		set _sum = _sum + _count;
		set _md5 = md5(_user_id);
		set _alias_id = -1;
		select id into _alias_id from alias a where a.md5 = _md5;
		if _alias_id > 0 then
			update alias set count = count + _count where id = _alias_id;
		else
			insert into alias (md5, name, count, github_user_id) values (_md5, _user_id, _count, _user_id);
		end if;
		set _idx = _idx + 1;
	end while;
	update repo_eval set contributor_count = _len, contributor_sum = _sum where repo_id = _repo_id;
	delete from repo_reserve where repo_id = _repo_id;
END