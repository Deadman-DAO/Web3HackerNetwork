DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`CreateRepoExtAssocTable`()
BEGIN
	drop table if exists repo_extension_association;

	create table repo_extension_association 
	(
		id int not null auto_increment primary key,
		repo_id int not null references repo(id),
		extension_id int not null references file_extension(id),
		count int not null default 0
	);
	create unique index repo_extension_composite on repo_extension_association(repo_id, extension_id);
END
/MANGINA/
DELIMITER ;
