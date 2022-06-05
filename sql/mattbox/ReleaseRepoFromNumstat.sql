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
	declare _commit_id char(40) default Null;

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
				select json_value(_commit, '$.cid') into _commit_id;			
				if exists(select id from commit where commit_id = _commit_id) THEN 
					if exists(select * from alias where id = _new_alias_id and github_user_id is null) and 
					   exists(select * from commit c join alias a on a.id = c.alias_id where c.commit_id = _commit_id and github_user_id is not null) THEN 
					   /* Okay - does this *new* record still not have a github_user_id, 
					    * *and* does the pre-existing commit record point to an alias that *does* have a github user Id
					    * If all this is true, then copy the github user id.  Yikes!
					    */
						update alias set github_user_id = (select a.github_user_id from commit c join alias a on a.id = c.alias_id where c.commit_id = _commit_id)
							where id = _new_alias_id;
					end if;
				else
					insert into commit(commit_id, alias_id, date, gmt_offset)
					 select _commit_id, _new_alias_id, FROM_UNIXTIME(json_value(_commit, '$.dt')), json_value(_commit, '$.tz');
				end if;
				set _commit_key_idx = _commit_key_idx + 1;
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