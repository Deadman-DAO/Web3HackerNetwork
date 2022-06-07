CREATE PROCEDURE w3hacknet.StoreForLater(
in _md5 char(32),
in _name_email varchar(256),
in _commit_count int,
in _min_date datetime,
in _max_date datetime,
in _commit_array json
)
BEGIN
	insert into hacker_update_queue (md5, name_email, commit_count, min_date, max_date, commit_array) values (_md5, _name_email, _commit_count, _min_date, _max_date, _commit_array);
END