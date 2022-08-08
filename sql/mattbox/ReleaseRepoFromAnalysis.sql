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
	declare _extension_val varchar(64);
	declare _extension_count int;
	declare _count int;
	
	call debug('Starting ReleaseFromRepoAnalysis!');
	update repo set last_analysis_date = dt, failed_date = case when _success then null else dt end
	 where id = _repo_id;
	update repo_reserve set tstamp = dt where repo_id = _repo_id;	
	insert into repo_numstat (repo_id, tstamp, numstat) values (_repo_id, dt, _numstat)
		on DUPLICATE key update tstamp = dt, numstat = _numstat;
	select json_query(_stats_json, '$.hacker_extension_map') into _hacker_extension_map;
#	call debug(_stats_json);
#	call debug(_hacker_extension_map);
	select json_query(_stats_json, '$.hacker_name_map') into _hacker_name_map;
	select json_query	(_stats_json, '$.extension_map') into _repo_extension_map;
	select json_keys(_hacker_name_map) into _keys;
	call debug(concat('Hacker keys: ', _keys));
	select json_length(_keys) into _array_size;
	while idx < _array_size do
		select json_value(_keys, concat('$[', idx, ']')) into _key;
		select json_value(_hacker_name_map, concat('$.', _key)) into _val;
		call debug(concat('md5 ', _key, ' -> ', _val));
		insert into hacker_update_queue (md5, name_email) select _key, _val;
		select id into _alias_pk from alias where md5 = _key;
		select json_query(_hacker_extension_map, concat('$.', _key)) into _extension_set;
		select json_keys(_extension_set) into _extension_keys;
		select json_length(_extension_keys) into _extension_len;
		while _ext_idx < _extension_len do
			select json_value(_extension_keys, concat('$[', _ext_idx, ']')) into _extension_val;
			select json_value(_extension_set, concat('$.', _extension_val)) into _extension_count;
			call debug(concat(_key, '->', _extension_val, _extension_count));
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
		call UpdateRepoExtensionCount(_repo_id, _key, _count);
		set idx = idx + 1;
	end while;
END
/MANGINA/
DELIMITER ;
