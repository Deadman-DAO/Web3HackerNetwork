use w3hacknet
drop table repo
create table repo (
	id int not null auto_increment primary key,
	owner varchar(64) not null,
	name varchar(64) not null 
)

create unique index repoIdx on repo(owner, name)

