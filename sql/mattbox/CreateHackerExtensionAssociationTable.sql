DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`CreateHackerExtensionAssociationTable`()
BEGIN
	drop table if exists hacker_extension_association;

	create table hacker_extension_association 
	(
		id int not null auto_increment primary key,
		alias_id int not null references alias(id),
		extension_id int not null references file_extension(id),
		count int not null default 0
	);
	create unique index alias_extension_composite on hacker_extension_association(alias_id, extension_id);
END
/MANGINA/
DELIMITER ;
