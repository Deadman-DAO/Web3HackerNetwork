DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`StoreForLater` (
IN _md5 char(32),
IN _name_email varchar(256),
IN _commit_count int(11),
IN _min_date datetime,
IN _max_date datetime,
IN _commit_array longtext
)
BEGIN
	insert into hacker_update_queue (md5, name_email, commit_count, min_date, max_date, commit_array) values (_md5, _name_email, _commit_count, _min_date, _max_date, _commit_array);
END
/MANGINA/
DELIMITER ;
