CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`CalcStats`()
BEGIN
	declare tm datetime default now();
	select count(*) into @alias_count from alias;
	select count(*) into @unresolved_alias_count from alias a where a.github_user_id is null;
	select count(*) into @unresolvable_alias_count from alias a where a.github_user_id = '<UNABLE_TO_RESOLVE>';
	select count(*) into @repo_commit_count from repo_commit;
	select count(*) into @commit_stats_count from commit_stats;
	select count(*) into @log_count from log;
	select count(*) into @repo_count from repo;
	select count(*) into @commit_count from commit;
	select tm, @alias_count, @unresolved_alias_count, @unresolvable_alias_count, @commit_count, @commit_stats_count, @log_count, @repo_count, @repo_commit_count;

END