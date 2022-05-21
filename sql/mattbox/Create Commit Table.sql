use w3hacknet
drop table commit;
create table commit (
	id int not null AUTO_INCREMENT primary key, 
	commit_id char(40) not null, 
	alias_id int not null, 
	date datetime, 
	gmt_offset varchar(16)
	, constraint `wtf` foreign key (alias_id) references alias(id));
create unique index commitIdIdx on commit(commit_id);
