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