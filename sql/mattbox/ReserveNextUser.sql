DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ReserveNextUser` (
IN who_is_reserving varchar(64)
)
BEGIN
	declare success bit;
	declare github_user varchar(64) default null;
	declare alias_hash char(32) default null;

	select github_user_id, md5 into github_user, alias_hash from (
		select a.github_user_id, a.md5,  a.count from alias a
		left join alias_reserve ar on ar.alias_id  = a.id
		where github_user_id is not null
		and github_user_id != '<UNABLE_TO_RESOLVE>'
		and github_user_id not like '%[bot]%'
		and github_user_id not like '%-bot%'
		and ar.reserver is null
		and a.last_traced is null
		order by a.id asc
		limit 1 
	) as X;
	
	call ReserveAlias(alias_hash, who_is_reserving, success);
	if success then
		select github_user, alias_hash;
	end if;
END
/MANGINA/
DELIMITER ;
