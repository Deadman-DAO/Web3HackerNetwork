CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ReleaseAlias`(
in alias_md5 char(32),
in user_who_reserved_it varchar(64))
BEGIN
	set @alias_id = -1;
	select id into @alias_id from alias where md5 = alias_md5;
	if @alias_id > 0 then
		call debug('Success!');
		delete from alias_reserve where alias_id = @alias_id and reserver = user_who_reserved_it;
	end if;
END