CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ReserveNextUser`(
in who_is_reserving varchar(64),
out github_user varchar(64),
out alias_hash char(32))
BEGIN
	declare success bit;

	select github_user_id, md5 into github_user, alias_hash from (
		select a.github_user_id, a.md5,  a.count, max(c.date), min(c.date) from alias a
		join commit c on c.alias_id = a.id
		left join alias_reserve ar on ar.alias_id  = a.id
		where github_user_id is not null
		and github_user_id not like '%[bot]%'
		and github_user_id not like '%-bot%'
		and ar.reserver is null
		group by a.github_user_id, a.md5, a.count
		order by 4 desc, 3 desc 
		limit 1 
	) as X;
	
	call ReserveAlias(alias_hash, who_is_reserving, success);
	if success = 0 then
		select null into github_user;
		select null into alias_hash;
	end if;
END