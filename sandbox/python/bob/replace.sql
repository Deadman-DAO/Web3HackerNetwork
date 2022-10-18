
select js.owner, js.repo_name,
  ifnull(js.total_inserts, 0) as js_inserts, ifnull(js.total_deletes, 0) as js_deletes,
    ifnull(js.num_files, 0) as js_files, ifnull(js.total_commits, 0) as js_commits,
  ifnull(py.total_inserts, 0) as py_inserts, ifnull(py.total_deletes, 0) as py_deletes,
    ifnull(py.num_files, 0) as py_files, ifnull(py.total_commits, 0) as py_commits,
  ifnull(c.total_inserts, 0) as c_inserts, ifnull(c.total_deletes, 0) as c_deletes,
    ifnull(c.num_files, 0) as c_files, ifnull(c.total_commits, 0) as c_commits,
  ifnull(java.total_inserts, 0) as java_inserts, ifnull(java.total_deletes, 0) as java_deletes,
    ifnull(java.num_files, 0) as java_files, ifnull(java.total_commits, 0) as java_commits,
  ifnull(go.total_inserts, 0) as go_inserts, ifnull(go.total_deletes, 0) as go_deletes,
    ifnull(go.num_files, 0) as go_files, ifnull(go.total_commits, 0) as go_commits,
  ifnull(ts.total_inserts, 0) as ts_inserts, ifnull(ts.total_deletes, 0) as ts_deletes,
    ifnull(ts.num_files, 0) as ts_files, ifnull(ts.total_commits, 0) as ts_commits,
  ifnull(cpp.total_inserts, 0) as cpp_inserts, ifnull(cpp.total_deletes, 0) as cpp_deletes,
    ifnull(cpp.num_files, 0) as cpp_files, ifnull(cpp.total_commits, 0) as cpp_commits,
  ifnull(php.total_inserts, 0) as php_inserts, ifnull(php.total_deletes, 0) as php_deletes,
    ifnull(php.num_files, 0) as php_files, ifnull(php.total_commits, 0) as php_commits,
  ifnull(rb.total_inserts, 0) as rb_inserts, ifnull(rb.total_deletes, 0) as rb_deletes,
    ifnull(rb.num_files, 0) as rb_files, ifnull(rb.total_commits, 0) as rb_commits,
  ifnull(cs.total_inserts, 0) as cs_inserts, ifnull(cs.total_deletes, 0) as cs_deletes,
    ifnull(cs.num_files, 0) as cs_files, ifnull(cs.total_commits, 0) as cs_commits,
  ifnull(cc.total_inserts, 0) as cc_inserts, ifnull(cc.total_deletes, 0) as cc_deletes,
    ifnull(cc.num_files, 0) as cc_files, ifnull(cc.total_commits, 0) as cc_commits,
  ifnull(rs.total_inserts, 0) as rs_inserts, ifnull(rs.total_deletes, 0) as rs_deletes,
    ifnull(rs.num_files, 0) as rs_files, ifnull(rs.total_commits, 0) as rs_commits,
  ifnull(tsx.total_inserts, 0) as tsx_inserts, ifnull(tsx.total_deletes, 0) as tsx_deletes,
    ifnull(tsx.num_files, 0) as tsx_files, ifnull(tsx.total_commits, 0) as tsx_commits,
  ifnull(scala.total_inserts, 0) as scala_inserts, ifnull(scala.total_deletes, 0) as scala_deletes,
    ifnull(scala.num_files, 0) as scala_files, ifnull(scala.total_commits, 0) as scala_commits,
  ifnull(jsx.total_inserts, 0) as jsx_inserts, ifnull(jsx.total_deletes, 0) as jsx_deletes,
    ifnull(jsx.num_files, 0) as jsx_files, ifnull(jsx.total_commits, 0) as jsx_commits
from repo_ext js
  left outer join repo_ext py on py.owner = js.owner and py.repo_name = js.repo_name
  left outer join repo_ext c on c.owner = js.owner and c.repo_name = js.repo_name
  left outer join repo_ext java on java.owner = js.owner and java.repo_name = js.repo_name
  left outer join repo_ext go on go.owner = js.owner and go.repo_name = js.repo_name
  left outer join repo_ext ts on ts.owner = js.owner and ts.repo_name = js.repo_name
  left outer join repo_ext cpp on cpp.owner = js.owner and cpp.repo_name = js.repo_name
  left outer join repo_ext php on php.owner = js.owner and php.repo_name = js.repo_name
  left outer join repo_ext rb on rb.owner = js.owner and rb.repo_name = js.repo_name
  left outer join repo_ext cs on cs.owner = js.owner and cs.repo_name = js.repo_name
  left outer join repo_ext cc on cc.owner = js.owner and cc.repo_name = js.repo_name
  left outer join repo_ext rs on rs.owner = js.owner and rs.repo_name = js.repo_name
  left outer join repo_ext tsx on tsx.owner = js.owner and tsx.repo_name = js.repo_name
  left outer join repo_ext scala on scala.owner = js.owner and scala.repo_name = js.repo_name
  left outer join repo_ext jsx on jsx.owner = js.owner and jsx.repo_name = js.repo_name
where js.extension = '.js'
  and py.extension = '.py'
  and c.extension = '.c'
  and java.extension = '.java'
  and go.extension = '.go'
  and ts.extension = '.ts'
  and cpp.extension = '.cpp'
  and php.extension = '.php'
  and rb.extension = '.rb'
  and cs.extension = '.cs'
  and cc.extension = '.cc'
  and rs.extension = '.rs'
  and tsx.extension = '.tsx'
  and scala.extension = '.scala'
  and jsx.extension = '.jsx'
order by js.owner, js.repo_name

