CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ReserveAlias`(
in alias_md5 char(32),
in reserver varchar(64),
out success bit
)
BEGIN
	declare ts datetime default now();
	set @alias_id = -1, success = 0;
	select id into @alias_id from alias where md5 = alias_md5;
	if @alias_id > -1 then
		insert ignore into alias_reserve (alias_id, tstamp, reserver) values (@alias_id, ts, reserver);
		if row_count() > 0 then
			set success = 1;
		end if;
	end if;
END