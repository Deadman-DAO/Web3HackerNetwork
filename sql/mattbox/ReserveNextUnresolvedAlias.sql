CREATE PROCEDURE w3hacknet.ReserveNextUnresolvedAlias
(
	in reserver_user_id varchar(32),
	out rslt_alias_id int,
	out commit_sample_json JSON
)
BEGIN
	declare dt datetime;
	declare _commit_id char(40);
	declare halfway_point datetime;
	select now() into dt;
	insert ignore alias_reserve (alias_id, tstamp, reserver)  
		select X.id, dt, reserver_user_id from ( 
			select a.id, a.md5, (max(c.date) - min(c.date))-(now() - max(c.date)) as sort_me from alias a
			left join alias_reserve ar on ar.alias_id = a.id
			join commit c on c.alias_id = a.id
			where ar.alias_id is null and a.github_user_id  is null
			and name not like '%[bot]%' and name not like '%-bot%'
			group by a.id, a.md5
			order by sort_me desc
			limit 1
		) as X;
	select alias_id into rslt_alias_id from alias_reserve where tstamp = dt and reserver = reserver_user_id limit 1;
	if rslt_alias_id is not null then
		set commit_sample_json = json_array();
		#Get NEWEST commit
		select commit_id into _commit_id from commit where alias_id = rslt_alias_id
		  order by date DESC 
		  limit 1;
		#insert into JSON array
		select json_insert(commit_sample_json, '$[0]', _commit_id) into commit_sample_json;

		#now calculate a middle point and find a commit near there
		select FROM_UNIXTIME( 
			((UNIX_TIMESTAMP(max(date))-UNIX_TIMESTAMP(min(date)))/2)+UNIX_TIMESTAMP(min(date)) 
			)
		  into halfway_point
		from commit where alias_id = rslt_alias_id;

		#insert into JSON array
		select json_insert(commit_sample_json, '$[1]', _commit_id) into commit_sample_json;

		#Get the OLDEST commit
		select commit_id into _commit_id from commit where alias_id = rslt_alias_id
		  order by date ASC
		  limit 1;
		#insert into JSON array
		select json_insert(commit_sample_json, '$[2]', _commit_id) into commit_sample_json;
	end if;
END