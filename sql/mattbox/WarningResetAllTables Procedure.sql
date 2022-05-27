CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`WarningResetALLTables`()
BEGIN
	drop table if exists repo_reserve;
	drop table if exists repo_commit;
	drop table if exists repo;
	drop table if exists commit_stats ;
	drop table if exists commit;
	drop table if exists alias_reserve;
	drop table if exists alias;
	drop table if exists log;
	drop table if exists db_update_queue;

	call CreateDBUpdateQueueTable();
	call createLogTable();

	create table alias (id int not null AUTO_INCREMENT primary key, md5 char(32) not null, name varchar(256), count int default 0, github_user_id varchar(64) default null);
	create unique index aliasIdx on alias (md5);

	call CreateAliasReserveTable();

	create table commit (
		id int not null AUTO_INCREMENT primary key, 
		commit_id char(40) not null, 
		alias_id int not null, 
		date datetime, 
		gmt_offset varchar(16)
		, constraint `wtf` foreign key (alias_id) references alias(id));
	create unique index commitIdIdx on commit(commit_id);

	create table commit_stats (
		id int not null AUTO_INCREMENT primary key, 
		commit_id int not null, 
		file_type varchar(128),
		insert_count int,
		delete_count int,
		occurrence_count int
		, constraint `xelda` foreign key (commit_id) references commit(id));
	create unique index commit_stats_Idx on commit_stats(id);
	create index commit_stats_fileType_idx on commit_stats(file_type);

	create table repo (
		id int not null auto_increment primary key,
		owner varchar(128) not null,
		name varchar(128) not null,
		commit_count int(11),
		min_date datetime,
		max_date datetime
	);

	create unique index repoIdx on repo(owner, name);

	CREATE TABLE `repo_commit` (
	  `id` int(11) NOT NULL AUTO_INCREMENT,
	  `commit_id` int(11) NOT NULL,
	  `repo_id` int(11) NOT NULL,
	  PRIMARY KEY (`id`),
	  KEY `weird` (`commit_id`),
	  KEY `weirder` (`repo_id`),
	  CONSTRAINT `weird` FOREIGN KEY (`commit_id`) REFERENCES `commit` (`id`),
	  CONSTRAINT `weirder` FOREIGN KEY (`repo_id`) REFERENCES `repo` (`id`)
	) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;

	call CreateRepoReserveTable();

END