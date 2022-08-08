DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`PracticeJsonParsing`()
BEGIN
	declare _hacker_extension_map longblob;
	declare _hacker_name_map longblob;
	declare _repo_extension_map longblob;
	declare _keys longblob;
	declare idx int default 0;
	declare _array_size int default 0;
	declare _key char(32);
	declare _val varchar(128);
	drop temporary table if exists _name_map;
	select message into _hacker_extension_map from log where id = 1205655;
	select message into _hacker_name_map from log where id = 1205656;
	select message into _repo_extension_map from log where id = 1205657;
	create temporary table _name_map (md5 char(32), name varchar(128));
	select json_keys(_hacker_name_map) into _keys;
	select json_length(_keys) into _array_size;
	while idx < _array_size do
		select json_value(_keys, concat('$[', idx, ']')) into _key;
		select json_value(_hacker_name_map, concat('$.', _key)) into _val;
		insert into _name_map (md5, name) select _key, _val;
		set idx = idx + 1;
	end while;		

	select * from _name_map;

END
/MANGINA/
DELIMITER ;
