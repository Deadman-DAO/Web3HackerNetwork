CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`addUpdateRepo`(
in owner_name varchar(128),
in repo_name varchar(128),
in commit_date datetime,
in commit_tz varchar(16),
in commit_hash char(40),
in auth_hash char(32))
BEGIN
	declare _min_date datetime default null;
	declare _max_date datetime default null;
	declare cnt int default 0;
	declare repo_id int default -1;
	declare message datetime;

select id, commit_count, min_date, max_date into repo_id, cnt, _min_date, _max_date from repo where owner = owner_name and name = repo_name;
	if repo_id < 1 then
		insert into repo (owner, name, commit_count, min_date, max_date) values (owner_name, repo_name, 1, commit_date, commit_date);
	else
		update repo set commit_count = commit_count + 1,
			min_date = 
				case 
					when ISNULL(_min_date) then commit_date
					else least(_min_date, commit_date)
				END,
			max_date =
				CASE
					when isnull(_max_date) then commit_date
					else GREATEST(_max_date, commit_date)
				end
		 where id = repo_id;
	end if;
	call insertCommit(owner_name, repo_name, commit_hash, auth_hash, null, commit_date, commit_tz, null, null);
END