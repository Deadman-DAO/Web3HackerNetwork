cols_tmpl = """  ifnull(@@ext@@.total_inserts, 0) as @@ext@@_inserts, ifnull(@@ext@@.total_deletes, 0) as @@ext@@_deletes,
    ifnull(@@ext@@.num_files, 0) as @@ext@@_files, ifnull(@@ext@@.total_commits, 0) as @@ext@@_commits"""

join_tmpl = """  left outer join repo_ext @@ext@@ on @@ext@@.owner = js.owner and @@ext@@.repo_name = js.repo_name"""

and_tmpl = "  and @@ext@@.extension = '.@@ext@@'"

def convert(tmpl, ext):
    return tmpl.replace('@@ext@@', ext)

summary_sql = f"""
select js.owner, js.repo_name,
{convert(cols_tmpl, 'js')},
{convert(cols_tmpl, 'py')},
{convert(cols_tmpl, 'c')},
{convert(cols_tmpl, 'java')},
{convert(cols_tmpl, 'go')},
{convert(cols_tmpl, 'ts')},
{convert(cols_tmpl, 'cpp')},
{convert(cols_tmpl, 'php')},
{convert(cols_tmpl, 'rb')},
{convert(cols_tmpl, 'cs')},
{convert(cols_tmpl, 'cc')},
{convert(cols_tmpl, 'rs')},
{convert(cols_tmpl, 'tsx')},
{convert(cols_tmpl, 'scala')},
{convert(cols_tmpl, 'jsx')}
from repo_ext js
{convert(join_tmpl, 'py')}
{convert(join_tmpl, 'c')}
{convert(join_tmpl, 'java')}
{convert(join_tmpl, 'go')}
{convert(join_tmpl, 'ts')}
{convert(join_tmpl, 'cpp')}
{convert(join_tmpl, 'php')}
{convert(join_tmpl, 'rb')}
{convert(join_tmpl, 'cs')}
{convert(join_tmpl, 'cc')}
{convert(join_tmpl, 'rs')}
{convert(join_tmpl, 'tsx')}
{convert(join_tmpl, 'scala')}
{convert(join_tmpl, 'jsx')}
where js.extension = '.js'
{convert(and_tmpl, 'py')}
{convert(and_tmpl, 'c')}
{convert(and_tmpl, 'java')}
{convert(and_tmpl, 'go')}
{convert(and_tmpl, 'ts')}
{convert(and_tmpl, 'cpp')}
{convert(and_tmpl, 'php')}
{convert(and_tmpl, 'rb')}
{convert(and_tmpl, 'cs')}
{convert(and_tmpl, 'cc')}
{convert(and_tmpl, 'rs')}
{convert(and_tmpl, 'tsx')}
{convert(and_tmpl, 'scala')}
{convert(and_tmpl, 'jsx')}
order by js.owner, js.repo_name
"""
print(summary_sql)

