CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`addUpdateRepo`(
in _owner_name varchar(128),
in _repo_name varchar(128),
in _commit_min_date datetime,
in _commit_max_date datetime,
in _commit_count int
)
BEGIN
	declare _min_date datetime default null;
	declare _max_date datetime default null;
	declare _cnt int default 0;
	declare _repo_id int default -1;
	declare _dt datetime default current_timestamp(3);

	select id, commit_count, min_date, max_date into _repo_id, _cnt, _min_date, _max_date from repo where owner = _owner_name and name = _repo_name;
	if _repo_id < 1 then
		insert into repo (owner, name, commit_count, min_date, max_date, last_updated) values (_owner_name, _repo_name, _commit_count, _commit_min_date, _commit_max_date, _dt);
	else
		update repo set commit_count = commit_count + _commit_count,
			last_updated = _dt,
			min_date = 
				case 
					when ISNULL(_min_date) then _commit_min_date
					else least(_min_date, _commit_min_date)
				END,
			max_date =
				CASE
					when isnull(_max_date) then _commit_max_date
					else GREATEST(_max_date, _commit_max_date)
				end
		 where id = _repo_id;
	end if;
END