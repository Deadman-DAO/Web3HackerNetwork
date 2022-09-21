DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ReleaseRepoFromAnalysisTwo` (
IN _repo_id int(11),
IN _success bit(1),
IN _stats_json longblob
)
BEGIN
	declare _perf_track_id int;
	declare dt datetime default now(3);

	update repo set last_analysis_date = dt, failed_date = case when _success then null else dt end
	 where id = _repo_id;
	update repo_reserve set tstamp = dt where repo_id = _repo_id;	
	insert into import_performance_tracking (repo_id, success, stats_json, starttime)
		select _repo_id, _success, _stats_json, dt;
	select LAST_INSERT_ID() into _perf_track_id; 

	insert into hacker_update_queue (md5, name_email, repo_owner, repo_name, file_extension, file_extension_count)
	    select tbl.hacker_hash, tbl.hacker_name, repo.repo_owner, repo.repo_name,  tbl.ext, tbl.cnt from
	    json_table(_stats_json, '$.hack_assoc_map[*]' columns (
	        hacker_hash char(32) path '$.hacker_hash',
	        hacker_name varchar(128) path '$.hacker_name',
	        nested path '$.hacker_extension_map[*]' columns (
	            ext varchar(64) path '$.ext',
	            cnt int path '$.cnt'
	        )
	    )) as tbl,
	    json_table(_stats_json, '$' columns (
	        repo_owner varchar(128) path '$.repo_owner',
	        repo_name varchar(128) path '$.repo_name'
	    )) as repo;
	
	/* now the imports (tied to the language extension e.g. .py) */
	insert into hacker_update_queue (md5, name_email, repo_owner, repo_name, import_lang_ext, import_name, import_contributions)
	    select tbl.hacker_hash, tbl.hacker_name, repo.repo_owner, repo.repo_name,  tbl.lang_ext, tbl.name, tbl.contributions from
	    json_table(_stats_json, '$.hack_assoc_map[*]' columns (
	        hacker_hash char(32) path '$.hacker_hash',
	        hacker_name varchar(128) path '$.hacker_name',
	        nested path '$.hacker_import_array[*]' columns (
	            lang_ext varchar(64) path '$.lang_ext',
	            nested path '$.import_map[*]' columns (
	                name varchar(256) path '$.name',
	                contributions double path '$.contributions'
	            )
	        )
	    )) as tbl,
	    json_table(_stats_json, '$' columns (
	        repo_owner varchar(128) path '$.repo_owner',
	        repo_name varchar(128) path '$.repo_name'
	    )) as repo;
    update import_performance_tracking set endtime = now(3) where id = _perf_track_id;
END
/MANGINA/
DELIMITER ;
