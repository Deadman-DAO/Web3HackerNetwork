project_root=/opt/deadman/Web3HackerNetwork
export PYTHONPATH=$project_root/python
cd $project_root/active
nohup python3 -u $PYTHONPATH/lib/scalable_repo_tasks.py >./scale.out &
