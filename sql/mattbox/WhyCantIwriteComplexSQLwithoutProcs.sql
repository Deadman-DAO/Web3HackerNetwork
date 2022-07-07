DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`WhyCantIwriteComplexSQLwithoutProcs`
BEGIN
	declare _idx int default 1;
	declare _rec_count int default 0;
	declare _commit_id int default -1;
	declare _alias_id  int default -1;

	create or replace temporary table orphan_alias (id int not null auto_increment primary key, commit_id int, alias_id int);
	create or replace temporary table just_alias(id int not null auto_increment primary key, alias_id int);
	create index _idx_1 on just_alias(alias_id);
	create index _idx_2 on orphan_alias(alias_id);
	
	insert into orphan_alias (commit_id, alias_id)
	select c.id, c.alias_id from commit c
	left join repo_commit rc on rc.commit_id = c.id 
	where rc.id is NULL;
	
	set _idx = 1;
	select count(*) into _rec_count from orphan_alias;
	while _idx <= _rec_count do
		select commit_id, alias_id into _commit_id, _alias_id from orphan_alias where id = _idx;
		call debug(concat('deleting commit ID', _commit_id));
		delete from commit where id = _commit_id;
		set _idx = _idx + 1;
	end while;
	
	insert into just_alias (alias_id) select distinct(alias_id) from orphan_alias;
	
	set _idx = 1;
	select count(*) into _rec_count from just_alias;
	while _idx <= _rec_count do
		select alias_id into _alias_id from just_alias where id = _idx;
		if not exists (select * from commit where alias_id = _alias_id) THEN 
			call debug(concat('Deleting alias id ', _alias_id));
			delete from alias where id = _alias_id and github_user_id is null;
		end if;
		set _idx = _idx + 1;
	end while;
	
END
/MANGINA/
DELIMITER ;
