DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`CreateNumstatTable`()
BEGIN
	drop table if exists repo_numstat;

	create table repo_numstat
	(
		id int not null auto_increment primary key,
		repo_id int unique not null, 
		tstamp datetime, 
		numstat longblob, 
		foreign key (repo_id) references repo(id)
	);
	
END
/MANGINA/
DELIMITER ;
