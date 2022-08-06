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
	update repo set last_analysis_date = dt, failed_date = case when _success then null else dt end
	 where id = _repo_id;
	update repo_reserve set tstamp = dt where repo_id = _repo_id;	
	insert into repo_numstat (repo_id, tstamp, numstat) values (_repo_id, dt, _numstat)
		on DUPLICATE key update tstamp = dt, numstat = _numstat;
	select json_value(_stats_json, '$.hacker_extension_map') into _hacker_extension_map;
	select json_value(_stats_json, '$.hacker_name_map') into _hacker_name_map;
	select json_value(_stats_json, '$.extension_map') into _repo_extension_map;
	call debug(_hacker_extension_map);
	call debug(_hacker_name_map);
	call debug(_repo_extension_map);

END
/MANGINA/
DELIMITER ;
