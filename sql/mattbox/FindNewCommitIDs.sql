DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`FindNewCommitIDs` (
IN _json_array longtext
)
BEGIN
	declare _idx int;
	declare _max int;
	declare _next_commit varchar(128);
	select json_length(_json_array) into _max;
	select 0 into _idx;

	create or replace temporary table _result (commit_id varchar(40));
	
	while _idx < _max do	
		select json_value(_json_array, concat('$[', _idx, ']')) into _next_commit;
		if not exists (select id from commit where commit_id = _next_commit) then
			insert into _result select _next_commit;
		end if;
		set _idx = _idx + 1;
	end while;
	select commit_id from _result;
END
/MANGINA/
DELIMITER ;
