CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`CalcStats`()
BEGIN
	declare tm datetime default now();
	select count(*) into @alias_count from alias;
	select count(*) into @repo_commit_count from repo_commit;
	select count(*) into @commit_stats_count from commit_stats;
	select count(*) into @log_count from log;
	select count(*) into @repo_count from repo;
	select count(*) into @commit_count from commit;
	select tm, @alias_count, @commit_count, @commit_stats_count, @log_count, @repo_count, @repo_commit_count;

END