DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`UpdateHacker` (
IN _md5 char(32),
IN _name_email varchar(256),
IN _commit_count int(11),
IN _min_date datetime,
IN _max_date datetime,
IN _repo_owner varchar(128),
IN _repo_name varchar(128),
IN _commit_array longtext,
IN _file_extension varchar(64),
IN _file_extension_count int(11),
IN _import_lang_ext varchar(64),
IN _import_name varchar(256),
IN _import_contributions float
)
BEGIN
	declare _alias_id int default null;
	declare _commit_count int default 0;
	declare _commit_array_size int default 0;
	declare _commit json;
	declare _commit_key_idx int default 0;
	declare _commit_id char(40);
	declare _repo_id int default -1;
	declare _new_commit_pri_key int default -1;
	declare _file_extension_pk int;

	if exists (select id from alias a where a.md5 = _md5) THEN 
		select id into _alias_id from alias a where a.md5 = _md5;
		update alias set count = count + _commit_count where id = _alias_id;
	else
		insert into alias (md5, name, count) values (_md5, _name_email, _commit_count);
		select LAST_INSERT_ID() into _alias_id;
		call debug(concat('New alias id is ', _alias_id));
	end if;
	
	if _commit_array is not null and exists (select * from alias a where a.id = _alias_id and a.github_user_id is null) THEN 
		select count(*) into _commit_count from commit c where c.alias_id = _alias_id;
		if _commit_count < 3 then
			set _commit_array_size = json_length(_commit_array);
			if _commit_array_size > _commit_count then
				set _commit_key_idx = 0;
				while _commit_key_idx < json_length(_commit_array) DO
					set _commit = json_query(_commit_array, concat('$[',_commit_key_idx,']'));
					select json_value(_commit, '$.cid') into _commit_id;
					if exists(select id from commit where commit_id = _commit_id) THEN 
						if exists(select * from alias where id = _alias_id and github_user_id is null) and 
						   exists(select * from commit c join alias a on a.id = c.alias_id where c.commit_id = _commit_id and github_user_id is not null) THEN 
						   
						   call debug(concat('Found an alternative ID for ', _md5, _name_email, _commit_key_idx));
							update alias set github_user_id = (select a.github_user_id from commit c join alias a on a.id = c.alias_id where c.commit_id = _commit_id)
								where id = _alias_id;
						end if;
					else
						insert into commit(commit_id, alias_id, date, gmt_offset)
						 select _commit_id, _alias_id, FROM_UNIXTIME(json_value(_commit, '$.dt')), json_value(_commit, '$.tz');
						select LAST_INSERT_ID() into _new_commit_pri_key;
						select id into _repo_id from repo where owner = _repo_owner and name = _repo_name;
						if _repo_id = -1 then
							insert into repo (owner, name, commit_count, min_date, max_date) values (_repo_owner, _repo_name, _commit_count, _min_date, _max_date);
							select LAST_INSERT_ID() into _repo_id;
						end if;
						insert into repo_commit (commit_id, repo_id) values (_new_commit_pri_key, _repo_id);
							
					end if;
					set _commit_key_idx = _commit_key_idx + 1;
				end while;
			end if;
		end if;
	end if;
	if ifnull(_file_extension_count, -1) > 0 and _file_extension is not null then
		call updateHackerExtensionCount(_alias_id, _file_extension, _file_extension_count);
	end if;
	if _import_lang_ext is not null and 
	   _import_name is not null and 
	   _import_contributions is not null 
    THEN
    	call UpdateHackerImportCount(_md5, _import_name, _import_lang_ext, _import_contributions);
	end if;
END
/MANGINA/
DELIMITER ;
