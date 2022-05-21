CREATE DEFINER=`matt`@`localhost` 
PROCEDURE `w3hacknet`.`InsertCommit`(
	owner_id varchar(128), 
	repo_name varchar(128), 
	commit_hash char(40), 
	author_hash char(32), 
	author_alias varchar(1024),
	date datetime, 
	orig_timezone varchar(16),
	file_types json)
	MODIFIES SQL DATA
BEGIN
	declare alias_id int default -1;
	declare commit_id int default -1;
	declare repo_id int default -1;
	declare repo_commit_id int default -1;
	declare key_idx int default 0; 
	declare extension varchar(1024);
	declare val varchar(256);
	declare inserts int default 0;
	declare deletes int default 0;
	declare occurrences int default 0;
	declare extension_set json;

	select -1 into alias_id;
	select id into alias_id from w3hacknet.alias where md5 = author_hash;
	if alias_id < 0 then
		insert into alias (md5, name, count) values (author_hash, left(author_alias, 256), 1);
		select LAST_INSERT_ID() into alias_id;
	else
		update w3hacknet.alias set count = count + 1 where id = alias_id;
	END IF; 
	
	select c.id into commit_id from commit c where c.commit_id = commit_hash ; 
	if commit_id = -1 THEN
		insert into commit (commit_id, alias_id, date, gmt_offset) values (commit_hash, alias_id, date, orig_timezone) ;
		select LAST_INSERT_ID() into commit_id;
	END IF;

	select -1 into repo_id;
	select id into repo_id from repo where owner = owner_id and name = repo_name;
	if repo_id = -1 then
		insert into repo (owner, name) values (owner_id, repo_name);
		select LAST_INSERT_ID() into repo_id;
	END IF;
	
    select id into repo_commit_id from repo_commit where commit_id = commit_Id and repo_id = repo_id;

	if repo_commit_id = -1 then
		insert into repo_commit (commit_id, repo_id) select commit_id, repo_id;
		/* no need to insert commit_stats if that repo_commit reference is already there */
		select json_keys(file_types) into extension_set;
		while key_idx < json_length(extension_set) do
			select json_value(extension_set, concat('$[',key_idx,']')) into extension;
			select json_query(file_types, concat('$.',extension)) into val;
			select json_value(val, '$.inserts') into inserts;
			select json_value(val, '$.deletes') into deletes;
			select json_value(val, '$.occurrences') into occurrences;
			insert into commit_stats (commit_id, file_type, insert_count, delete_count, occurrence_count)
				select commit_id, left(extension, 128), inserts, deletes, occurrences;
				
			set key_idx = key_idx + 1;
		end WHILE;
	End IF;


END