DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`CreateFileExtensionTable`()
BEGIN
	drop table if exists file_extension;
	create table file_extension (
		id int not null auto_increment primary key,
		ext varchar(64) not null,
		description varchar(256)
	);
	create unique index ext_idx on file_extension(ext);
END
/MANGINA/
DELIMITER ;
