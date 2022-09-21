DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`Test_ReleaseRepoFromAnalysisTwo`()
BEGIN

	declare _start_time timestamp(3);
	declare _end_time datetime(3);
	declare _repo_id int;
	declare _json json;

	set _json = '{"repo_owner":"deepaksilokaofficial","repo_name":"AKS","hack_assoc_map":[{"hacker_hash":"33b1c3d4bc35df4b4ca055006dcf495d","hacker_name":"deepaksilokaofficial <58412342+deepaksilokaofficial@users.noreply.github.com>","hacker_extension_map":[{"ext":"md","cnt":3},{"ext":"yml","cnt":1},{"ext":"noexttext","cnt":3},{"ext":"txt","cnt":1}],"hacker_import_array":[{"lang_ext":"py","import_map":[{"name":"os","contributions":13.5674},{"name":"json","contributions":7.98124}]}]},{"hacker_hash":"a9a400aa2d5f7afb23e68899d3aca144","hacker_name":"deepaksilokaofficial <deepaksiloka@gmail.com>","hacker_extension_map":[{"ext":"py","cnt":3162},{"ext":"csv","cnt":15},{"ext":"pkl","cnt":12},{"ext":"csh","cnt":1}],"hacker_import_array":[{"lang_ext":"py","import_map":[{"name":"os","contributions":113.5674},{"name":"json","contributions":107.98124}]}]}]}';
	set _repo_id = 397485;  /* deepaksilokaofficial/AKS */
	select now(3) into _start_time;
	call ReleaseRepoFromAnalysisTwo(_repo_id, 1, _json); 
	select now(3) into _end_time;
	call debug(concat('Processed repo ', _repo_id, '.  Start time ', _start_time, ' End Time ', _end_time, ' diff ', timestampdiff(microsecond, _start_time, _end_time)/1000000));
END
/MANGINA/
DELIMITER ;
