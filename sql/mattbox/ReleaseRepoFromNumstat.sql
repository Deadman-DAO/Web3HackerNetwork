CREATE PROCEDURE w3hacknet.ReleaseRepoFromNumstat(	
in _repo_id int,
in _numstat_machine_name varchar(64),
in _numstat_dir varchar(128),
in _author_list json
)
BEGIN
	declare dt datetime default now();
	declare _tran_count int default 0;
	declare _file_count int default 0;
	declare _min_date datetime default now();
	declare _max_date datetime default FROM_UNIXTIME(0);
	declare _author varchar(256);
	declare _md5 char(32);
	declare _key_idx int default 0;
	declare _commit_key_idx int default 0;
	declare _elem json;
	declare _commit_array json;
	declare _commit json;
	declare _new_alias_id int;
	declare _try_date datetime;
	declare _auth_tran_count int default 0;

	call debug(concat('json_length of _author_list is ', json_length(_author_list)));
	while _key_idx < json_length(_author_list) DO
		select json_query(_author_list, concat('$[',_key_idx,']')) into _elem;
		select json_value(_elem, '$.name_email') into _author;
		select json_value(_elem, '$.md5') into _md5 ;
		set _try_date = FROM_UNIXTIME(json_value(_elem, '$.min_date'));
		if _try_date < _min_date then
			set _min_date = _try_date;
		end if;
		set _try_date = FROM_UNIXTIME(json_value(_elem, '$.max_date'));
		if _try_date > _max_date then
			set _max_date = _try_date;
		end if;
		set _auth_tran_count = json_value(_elem, '$.commit_count');
		set _tran_count = _tran_count + _auth_tran_count;
		if not exists (select id from alias a where a.md5 = _md5) THEN 
			insert into alias (md5, name, count) values (_md5, _author, _auth_tran_count);
			set _new_alias_id = LAST_INSERT_ID(); 
			select json_query(_elem, '$.last_ten') into _commit_array;
			set _commit_key_idx = 0;
			while _commit_key_idx < json_length(_commit_array) DO
				set _commit = json_query(_commit_array, concat('$[',_commit_key_idx,']'));
				insert into commit(commit_id, alias_id, date, gmt_offset)
				 select json_value(_commit, '$.cid'), _new_alias_id, FROM_UNIXTIME(json_value(_commit, '$.dt')), json_value(_commit, '$.tz');
			end while;
		end if;
		set _key_idx = _key_idx + 1;
	end while;

	update repo set last_numstat_date = dt, 
		numstat_machine_name = _numstat_machine_name, 
		numstat_dir = _numstat_dir,
		commit_count = _tran_count,
		min_date = _min_date,
		max_date = _max_date,
		last_numstat_date = dt
	 where id = _repo_id;
	delete from repo_reserve where repo_id = _repo_id;	
END