BLAME_JOB = 1
DEPS_JOB = 2
FILE_HACKER_JOB = 4
REPO_FILE_JOB = 8
JOBS = DEPS_JOB | REPO_FILE_JOB

if JOBS & BLAME_JOB:
    print('error: should not include blame_job')
else:
    print('good')
if not (JOBS & DEPS_JOB):
    print('error: should include deps_job')
else:
    print('good')
if JOBS & FILE_HACKER_JOB:
    print('error: should not include file_hacker_job')
else:
    print('good')
if not (JOBS & REPO_FILE_JOB):
    print('error: should not include repo_file_job')
else:
    print('good')
