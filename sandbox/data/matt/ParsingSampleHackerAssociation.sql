set @xxx = '{"repo_owner":"deepaksilokaofficial","repo_name":"AKS","hack_assoc_map":[{"hacker_hash":"33b1c3d4bc35df4b4ca055006dcf495d","hacker_name":"deepaksilokaofficial <58412342+deepaksilokaofficial@users.noreply.github.com>","hacker_extension_map":[{"ext":"md","cnt":3},{"ext":"yml","cnt":1},{"ext":"noexttext","cnt":3},{"ext":"txt","cnt":1}],"hacker_import_array":[{"lang_ext":"py","import_map":[{"name":"os","contributions":13.5674},{"name":"json","contributions":7.98124}]}]},{"hacker_hash":"a9a400aa2d5f7afb23e68899d3aca144","hacker_name":"deepaksilokaofficial <deepaksiloka@gmail.com>","hacker_extension_map":[{"ext":"py","cnt":3162},{"ext":"csv","cnt":15},{"ext":"pkl","cnt":12},{"ext":"csh","cnt":1}],"hacker_import_array":[{"lang_ext":"py","import_map":[{"name":"os","contributions":113.5674},{"name":"json","contributions":107.98124}]}]}]}';
/* first the file extension associations */
insert into hacker_update_queue (md5, name_email, repo_owner, repo_name, file_extension, file_extension_count)
    select tbl.hacker_hash, tbl.hacker_name, repo.repo_owner, repo.repo_name,  tbl.ext, tbl.cnt from
    json_table(@xxx, '$.hack_assoc_map[*]' columns (
        hacker_hash char(32) path '$.hacker_hash',
        hacker_name varchar(128) path '$.hacker_name',
        nested path '$.hacker_extension_map[*]' columns (
            ext varchar(64) path '$.ext',
            cnt int path '$.cnt'
        )
    )) as tbl,
    json_table(@xxx, '$' columns (
        repo_owner varchar(128) path '$.repo_owner',
        repo_name varchar(128) path '$.repo_name'
    )) as repo

/* now the imports (tied to the language extension e.g. .py) */
insert into hacker_update_queue (md5, name_email, repo_owner, repo_name, import_lang_ext, import_name, import_contributions)
    select tbl.hacker_hash, tbl.hacker_name, repo.repo_owner, repo.repo_name,  tbl.lang_ext, tbl.name, tbl.contributions from
    json_table(@xxx, '$.hack_assoc_map[*]' columns (
        hacker_hash char(32) path '$.hacker_hash',
        hacker_name varchar(128) path '$.hacker_name',
        nested path '$.hacker_import_array[*]' columns (
            lang_ext varchar(64) path '$.lang_ext',
            nested path '$.import_map[*]' columns (
                name varchar(256) path '$.name',
                contributions double path '$.contributions'
            )
        )
    )) as tbl,
    json_table(@xxx, '$' columns (
        repo_owner varchar(128) path '$.repo_owner',
        repo_name varchar(128) path '$.repo_name'
    )) as repo

/* The hacker_update_queue table has a trigger on it that automatically calls the UpdateHacker procedure.
   UpdateHacker copes with the various data content combination and makes sure that all the necessary
   components are created if necessary and updated.
 */