use w3hacknet
drop table commit_stats;
create table commit_stats (
	id int not null AUTO_INCREMENT primary key, 
	commit_id int not null, 
	file_type varchar(128),
	insert_count int,
	delete_count int,
	occurrence_count int
	, constraint `xelda` foreign key (commit_id) references commit(id));
create unique index commit_stats_Idx on commit_stats(id);
create index commit_stats_fileType_idx on commit_stats(file_type);