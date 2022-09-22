import sys

sys.path.append("../../python/lib")
from db_dependent_class import DBDependent

'''
ToDo - capture scheduled events
e.g.
   create or replace event cleanup_hacker_update_queue on schedule every 1 HOUR 
   DO truncate hacker_update_queue

creates one information_schema.events record

select event_name, event_type, interval_value, interval_field, event_definition from information_schema.events 
produces:
    cleanup_hacker_update_queue	RECURRING	1	HOUR	truncate hacker_update_queue
    
Note: "set global event_scheduler=ON" must be executed to enable the scheduler
appended /etc/mysql/my.cfg with:
[mariadb]
event_scheduler=ON    
 
'''

class Param:
    def __init__(self, row):
        self.mode = row[2]
        self.name = row[3]
        self.data_type = row[5]


class Procedure:
    def __init__(self, proc_name):
        self.params = []
        self.proc_name = proc_name

    def add_parameter(self, row):
        self.params.append(Param(row))


class SaveSQL(DBDependent):
    def __init__(self):
        DBDependent.__init__(self)
        self.source_sql = """
        select routine_name,
               routine_definition as definition
        from information_schema.routines r
        where routine_schema = 'w3hacknet'
       order by routine_schema,
                 routine_name;
        """
        self.param_sql = """
        select specific_name, 
                ordinal_position, 
                parameter_mode, 
                parameter_name, 
                data_type, 
                dtd_identifier, 
                CHARACTER_MAXIMUM_LENGTH 
           from information_schema.PARAMETERS
          where SPECIFIC_SCHEMA = 'w3hacknet'
          order by specific_name, ordinal_position
        """
        self.trigger_Sql = """
        select 'create or replace trigger\n ', trigger_name, action_timing, event_manipulation, ' on ', event_object_table, 
               ' for each row ', action_statement
          from information_schema.TRIGGERS t 
"""
        self.database = None

    def main(self):
        c = self.get_cursor()
        procedure_map = {}
        c.execute(self.param_sql)
        for row in c.fetchall():
            proc_name = row[0]
            if proc_name in procedure_map.keys():
                procedure = procedure_map[proc_name]
            else:
                procedure = Procedure(proc_name)
                procedure_map[proc_name] = procedure
            procedure.add_parameter(row)

        c.execute(self.source_sql)
        for row in self.get_cursor().fetchall():
            proc_name = row[0]
            procedure = None
            procedure = procedure_map[proc_name] if proc_name in procedure_map.keys() else None
            with open('./'+proc_name+'.sql', 'wt') as w:
                print('Processing', proc_name)
                w.write("DELIMITER /MANGINA/\n")
                w.write("create or replace procedure `w3hacknet`.`"+proc_name+"`"+(" (\n" if procedure else "()\n"))
                if procedure:
                    size = len(procedure.params)
                    for idx in range(0, size):
                        p = procedure.params[idx]
                        w.write(p.mode+' '+p.name+' '+p.data_type+(',\n' if idx < (size - 1) else '\n)\n'))

                w.write(row[1].replace('\r', ''))
                w.write("\n/MANGINA/\n")
                w.write("DELIMITER ;\n")
        c.execute(self.trigger_Sql)
        for row in self.get_cursor().fetchall():
            trigger_name = row[1]
            with open('./'+trigger_name+'.sql', 'wt') as w:
                print('Processing trigger: ', trigger_name)
                w.write("DELIMITER /MANGINA/\n")
                for n in row:
                    w.write(n+"\n")
                w.write("/MANGINA/\n")
                w.write("DELIMITER ;\n")

        sys.exit(0)


if __name__ == "__main__":
    SaveSQL().main()