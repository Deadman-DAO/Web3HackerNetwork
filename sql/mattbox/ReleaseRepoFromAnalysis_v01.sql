DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ReleaseRepoFromAnalysis_v01` (
IN _repo_id int(11),
IN _success bit(1),
IN _stats_json longblob,
IN _error_message varchar(256),
IN _timed_out bit(1),
IN _repo_needs_eval bit(1)
)
BEGIN
	declare _randy float default rand();

	if _repo_needs_eval then
		insert into priority_repos_staged_for_eval (repo_id) values (_repo_id);
    end if;
    call ReleaseRepoFromAnalysis(_repo_id, _success, _stats_json, _error_message, _timed_out);
END
/MANGINA/
DELIMITER ;
