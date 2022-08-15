DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ReleaseRepoFromAnalysis` (
IN _repo_id int(11),
IN _numstat longblob,
IN _success bit(1),
IN _stats_json longblob
)
BEGIN
	declare dt datetime default current_timestamp(3);
	declare _hacker_extension_map longblob;
	declare _hacker_name_map longblob;
	declare _repo_extension_map longblob;
	declare _repo_import_map longblob;
	declare _import_map longblob;
	declare _keys longblob;
	declare idx int default 0;
	declare _array_size int default 0;
	declare _key char(32);
	declare _val varchar(128);
	declare _alias_pk int;
	declare _extension_set longblob;
	declare _extension_keys longblob;
	declare _extension_len int;
	declare _ext_idx int default 0;
	declare _import_set longblob;
	declare _import_keys longblob;
	declare _import_len int;
	declare _imp_idx int default 0;
	declare _import_count int;
	declare _import_val varchar(256);
	declare _extension_val varchar(64);
	declare _extension_count int;
	declare _count int;
	declare _import_sub_map longblob;
	declare _hacker_contributions float;
	declare _hacker_cont_keys longblob;
	declare _hacker_cont_keys_len int;
	declare _hacker_cont_idx int;
	declare _hacker_md5 char(32);

	
#	call debug('Starting ReleaseFromRepoAnalysis!');
	update repo set last_analysis_date = dt, failed_date = case when _success then null else dt end
	 where id = _repo_id;
	update repo_reserve set tstamp = dt where repo_id = _repo_id;	
	insert into repo_numstat (repo_id, tstamp, numstat) values (_repo_id, dt, _numstat)
		on DUPLICATE key update tstamp = dt, numstat = _numstat;
	select json_query(_stats_json, '$.hacker_extension_map') into _hacker_extension_map;
#	call debug(_stats_json);
#	call debug(_hacker_extension_map);
	select json_query(_stats_json, '$.hacker_name_map') into _hacker_name_map;
	select json_query(_stats_json, '$.extension_map') into _repo_extension_map;
	select json_query(_stats_json, '$.import_map_map') into _repo_import_map;
	select json_keys(_hacker_name_map) into _keys;
#	call debug(concat('Hacker keys: ', _keys));
	select json_length(_keys) into _array_size;
	while idx < _array_size do
		select json_value(_keys, concat('$[', idx, ']')) into _key;
		select json_value(_hacker_name_map, concat('$."', _key, '"')) into _val;
#		call debug(concat('md5 ', _key, ' -> ', _val));
		insert into hacker_update_queue (md5, name_email) select _key, _val;
		select id into _alias_pk from alias where md5 = _key;
		select json_query(_hacker_extension_map, concat('$.', _key)) into _extension_set;
		select json_keys(_extension_set) into _extension_keys;
		select json_length(_extension_keys) into _extension_len;
		while _ext_idx < _extension_len do
			select json_value(_extension_keys, concat('$[', _ext_idx, ']')) into _extension_val;
			select json_value(_extension_set, concat('$.', _extension_val)) into _extension_count;
#			call debug(concat(_key, '->', _extension_val, _extension_count));
			call UpdateHackerExtensionCount(_alias_pk, _extension_val, _extension_count);
			set _ext_idx = _ext_idx + 1;
		end while;
		set idx = idx + 1;
	end while;		
	select json_keys(_repo_extension_map) into _keys;
	select json_length(_keys) into _array_size;
	set idx = 0;
	while idx < _array_size do
		select json_value(_keys, concat('$[', idx, ']')) into _key;
		select json_value(_repo_extension_map, concat('$.', _key)) into _count;
#		call debug(concat('Repo:', _repo_id,' key=',_key,', cnt=',_count));
		call UpdateRepoExtensionCount(_repo_id, _key, _count);
		set idx = idx + 1;
	end while;
	select json_keys(_repo_import_map) into _keys;
	select json_length(_keys) into _array_size;
	set idx = 0;
	while idx < _array_size do
		select json_value(_keys, concat('$[', idx, ']')) into _extension_val;
		select json_query(_repo_import_map, concat('$.', _extension_val)) into _import_map;
		select json_keys(_import_map) into _import_keys;
		select json_length(_import_keys) into _import_len;
		set _imp_idx = 0;
		while _imp_idx < _import_len do
			select json_value(_import_keys, concat('$[', _imp_idx, ']')) into _import_val;
			call debug(concat('ReleaseRepoFromAnalysis: idx', _imp_idx, ' key ', _import_val));
			select json_query(_import_map, concat('$."', _import_val, '"')) into _import_sub_map;
			select json_value(_import_sub_map, '$.repo_count') into _import_count;
			call UpdateRepoImportCount(_repo_id, _import_val, _extension_val, _import_count);
			/* Now pull out the individual hacker contributions */
			select json_query(_import_sub_map, '$.hackers') into _hacker_contributions;
			select json_keys(_hacker_contributions) into _hacker_cont_keys;
			select json_length(_hacker_cont_keys) into _hacker_cont_keys_len;
			set _hacker_cont_idx = 0;
			while _hacker_cont_idx < _hacker_cont_keys_len do
				select json_value(_hacker_cont_keys, concat('$[', _hacker_cont_idx, ']')) into _hacker_md5;
				set _alias_pk = -1;
				select id into _alias_pk from alias where md5 = _hacker_md5;
				if _alias_pk > 0 then
					select json_value(_hacker_contributions, concat('$.', _hacker_md5)) into _hacker_contributions;
					call UpdateHackerImportCount(_alias_pk, _import_val, _extension_val, _hacker_contributions);
				else
					call debug(concat('UpdateHackerImportCount NOT called because ', _hacker_md5, ' was not found in alias table'));
				end if;
				set _hacker_cont_idx = _hacker_cont_idx + 1;
			end while;
			set _imp_idx = _imp_idx + 1;
		end while;
		set idx = idx + 1;
	end while;
END
/MANGINA/
DELIMITER ;
