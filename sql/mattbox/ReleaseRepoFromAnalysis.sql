DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ReleaseRepoFromAnalysis` (
IN _repo_id int(11),
IN _success bit(1),
IN _stats_json longblob
)
BEGIN
	declare dt datetime default current_timestamp(3);
	declare _hacker_extension_map longblob;
	declare _hacker_name_map longblob;
	declare _repo_extension_map longblob;
	declare _repo_import_map longblob;
	declare _language_map longblob;
	declare _import_map longblob;
	declare _keys longblob;
	declare idx int default 0;
	declare _array_size int default 0;
	declare _key char(40);
	declare _val varchar(128);
	declare _email_key varchar(256);
	declare _md5 char(32);
	declare _alias_pk int;
	declare _extension_set longblob;
	declare _extension_keys longblob;
	declare _extension_len int;
	declare _ext_idx int default 0;
	declare _import_set longblob;
	declare _import_keys longblob;
	declare _import_key varchar(256);
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
	declare _hacker_md5 char(40);
	declare _contributor_map longblob;
	declare _contrib_hash_array longblob;
	declare _contrib_array_len int;
	declare _contrib_idx int;
	declare _contributor_hash char(40);
	declare _hacker_contrib_pct_map longblob;
	declare _hacker_hash_array longblob;
	declare _hacker_hash_len int;
	declare _hacker_idx int;
	declare _hacker_hash char(32);
	declare _hacker_pct varchar(32);
	declare _perf_track_id int;

	
	update repo set last_analysis_date = dt, failed_date = case when _success then null else dt end
	 where id = _repo_id;
	update repo_reserve set tstamp = dt where repo_id = _repo_id;	
	insert into import_performance_tracking (repo_id, success, stats_json, starttime)
		select _repo_id, _success, _stats_json, dt;
	select LAST_INSERT_ID() into _perf_track_id; 
	select json_query(_stats_json, '$.hacker_extension_map') into _hacker_extension_map;
#	call debug(_stats_json);
#	call debug(_hacker_extension_map);
	select json_query(_stats_json, '$.hacker_name_map') into _hacker_name_map;
	select json_query(_stats_json, '$.extension_map') into _repo_extension_map;
	select json_query(_stats_json, '$.import_map_map') into _repo_import_map;
	select json_keys(_hacker_name_map) into _keys;
#	call debug(concat('Hacker keys: ', _keys));
	select json_length(_keys) into _array_size;
#	call debug(concat('There are ', _array_size, ' hacker keys'));
	set idx = 0;
	while idx < _array_size do
		select json_value(_keys, concat('$[', idx, ']')) into _md5;
#		call debug(concat('The _md5 is ', ifnull(_md5,'Nada!')));
		select json_value(_hacker_name_map, concat('$.', _md5)) into _email_key;
#		call debug(concat('md5 ', ifnull(_md5, '<NULL>'), ' -> ', _email_key));
		insert into hacker_update_queue (md5, name_email) select _md5, _email_key;
		select id into _alias_pk from alias where md5 = _md5;
		select json_query(_hacker_extension_map, concat('$.', _md5)) into _extension_set;
		select json_keys(_extension_set) into _extension_keys;
		select json_length(_extension_keys) into _extension_len;
		set _ext_idx = 0;
		while _ext_idx < _extension_len do
			select json_value(_extension_keys, concat('$[', _ext_idx, ']')) into _extension_val;
			select json_value(_extension_set, concat('$.', _extension_val)) into _extension_count;
#			call debug(concat(_md5, '->', _extension_val, ' qty: ', _extension_count));
			call UpdateHackerExtensionCount(_alias_pk, _extension_val, _extension_count);
			set _ext_idx = _ext_idx + 1;
		end while;
		set idx = idx + 1;
	end while;		
	update import_performance_tracking set hacker_name_map_size = _array_size, hacker_name_map_completion = CURRENT_TIMESTAMP(3)
	 where id = _perf_track_id;
#	call debug('Exiting hacker iteration loop');
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
	update import_performance_tracking set extension_map_size = _array_size, extension_map_completion = CURRENT_TIMESTAMP(3)
	 where id = _perf_track_id;

	#Now on to the import_map_map that contains a tree of:
	#  lang.contributors.single_file_instance_hash->dict[hacker_hash]->float (percentage of contribution (0->1))
	#  lang.imports.import_name->array_of_single_file_instance_hash
	select json_keys(_repo_import_map) into _keys;  #language keys
	select json_length(_keys) into _array_size; 	#How many different languages
#	call debug(concat('Processing language-specific imports for ', _array_size, ' different languages'));
	set idx = 0;
	while idx < _array_size do
		select json_value(_keys, concat('$[', idx, ']')) into _extension_val;
#		call debug(concat('Language extension: ', _extension_val));
	    #_extension_val is the root analysis language (e.g. py or java)
		select json_query(_repo_import_map, concat('$.', _extension_val)) into _language_map;
		#_language_map now contains a contributor map and an imports map
		select json_query(_language_map, '$.contributors') into _contributor_map;
		select json_query(_language_map, '$.imports') into _import_map;
	
		select json_keys(_import_map) into _import_keys;
		select json_length(_import_keys) into _import_len;
#		call debug(concat('Imports include ', _import_len, ' element(s)'));
		set _imp_idx = 0;
		while _imp_idx < _import_len do
			select json_value(_import_keys, concat('$[', _imp_idx, ']')) into _import_key;
#			call debug(concat('Index ', _imp_idx, ' produces ', _import_key));
			# Now _import_key is an import value like library.subset.thingy
			# Within the json doc this key references an array of md5-hash contributor keys
			select json_query(_import_map, concat('$."', _import_key, '"')) into _contrib_hash_array;
			select json_length(_contrib_hash_array) into _contrib_array_len;
			set _contrib_idx = 0;
			while _contrib_idx < _contrib_array_len do
				call UpdateRepoImportCount(_repo_id, _import_key, _extension_val, 1);
				select json_value(_contrib_hash_array, concat('$[', _contrib_idx, ']')) into _contributor_hash;
				select json_query(_contributor_map, concat('$."', _contributor_hash, '"')) into _hacker_contrib_pct_map;
#				call debug(concat('Contributor_hash ', _contributor_hash, ' produces ', _hacker_contrib_pct_map));
				select json_keys(_hacker_contrib_pct_map) into _hacker_hash_array;
				select json_length(_hacker_hash_array) into _hacker_hash_len;
				set _hacker_idx = 0;
				while _hacker_idx < _hacker_hash_len do
					select json_value(_hacker_hash_array, concat('$[', _hacker_idx, ']')) into _hacker_hash;
#					call debug(concat('_hacker_hash ', _hacker_hash));
					select json_value(_hacker_contrib_pct_map, concat('$."', _hacker_hash, '"')) into _hacker_pct;
#					call debug(concat('Hacker hash ', _hacker_hash, ' ImportKey ', _import_key, ' extension ', _extension_val, ' hack Pct ', _hacker_pct));
					call UpdateHackerImportCount(_hacker_hash, _import_key, _extension_val, cast(_hacker_pct as float));				
					set _hacker_idx = _hacker_idx + 1;
				end while;
				set _contrib_idx = _contrib_idx + 1;
			end while;
		
			set _imp_idx = _imp_idx + 1;
		end while;
		set idx = idx + 1;
	end while;
	update import_performance_tracking set import_map_map_size = _array_size, import_map_map_completion = CURRENT_TIMESTAMP(3), endtime = CURRENT_TIMESTAMP(3) 
	 where id = _perf_track_id;

END
/MANGINA/
DELIMITER ;
