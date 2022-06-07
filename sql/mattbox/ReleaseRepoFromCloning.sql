CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ReleaseRepoFromCloning`(
in _repo_id int,
in _machine_name varchar(64),
in _repo_dir varchar(128)
)
BEGIN
	declare dt datetime default now();
	update repo set repo_machine_name = _machine_name, repo_dir = _repo_dir, last_cloned_date = dt
	 where id = _repo_id;
	delete from repo_reserve where repo_id = _repo_id;
END