#!/usr/bin/env perl

my $cmd_num_files = 'find path/to/repo/ -type f ! -path \'*/.*\' | wc -l | awk \'{print "num_files\t"$1}\'';
my $cmd_num_commits = 'grep \'^Author: \' path/to/repo.txt | wc -l | awk \'{print "num_commits\t"$1}\'';
my $cmd_locs = 'find path/to/repo/ -type f ! -path \'*/.*\' | xargs file | egrep \' .*(ASCII|JSON|source|Unicode|text|perl)\' '
    .'| awk \'{print $1}\' | sed \'s/:$//\' | xargs wc -l | egrep -v \' total$\' | awk \'{print $1}\' '
    .'| perl -e \'$a=0;while(<>){chomp;$a+=$_;}print$a."\n";\' | awk \'{print "num_locs\t"$1}\'';
#'
my $cmd_num_rust_files = 'find path/to/repo/ -type f ! -path \'*/.*\' | egrep \'.rs$\' | wc -l | awk \'{print "num_rust_files\t"$1}\'';
#'
my $cmd_num_react_files = 'find path/to/repo/ -type f ! -path \'*/.*\' | egrep \'.[tj]sx?$\' | wc -l | awk \'{print "num_react_files\t"$1}\'';
#'
my $cmd_num_markdown_files = 'find path/to/repo/ -type f -path \'*.md\' ! -path \'*/.*\' | wc -l | awk \'{print "num_markdown_files\t"$1}\'';
#'
my $cmd_num_binary_files = 'find path/to/repo/ -type f ! -path \'*/.*\' | xargs file | egrep -v \' .*(ASCII|JSON|source|Unicode|text|perl)\' | awk \'{print $1}\' | sed \'s/:$//\' | wc -l | awk \'{print "num_binary_files\t"$1}\'';
#'
my $cmd_rust_locs = 'find path/to/repo/ -type f ! -path \'*/.*\' | egrep \'.rs$\' | xargs wc -l | perl -e \'$a=0;while(<>){chomp;$a+=$_;}print$a."\n";\' | awk \'{print "num_rust_locs\t"$1}\'';
#'
my $cmd_react_locs = 'find path/to/repo/ -type f ! -path \'*/.*\' | egrep \'.[tj]sx?$\' | xargs wc -l | perl -e \'$a=0;while(<>){chomp;$a+=$_;}print$a."\n";\' | awk \'{print "num_react_locs\t"$1}\'';
#'
my $cmd_markdown_locs = 'find path/to/repo/ -type f -path \'*.md\' ! -path \'*/.*\' | xargs wc -l | perl -e \'$a=0;while(<>){chomp;$a+=$_;}print$a."\n";\' | awk \'{print "num_markdown_locs\t"$1}\'';
#'
my $cmd_binary_bytes = 'find path/to/repo/ -type f ! -path \'*/.*\' | xargs file | egrep -v \' .*(ASCII|JSON|source|Unicode|text|perl)\' | awk \'{print $1}\' | sed \'s/:$//\' | xargs wc -c | egrep -v \' total$\' | awk \'{print $1}\' | perl -e \'$a=0;while(<>){chomp;$a+=$_;}print$a."\n";\' | awk \'{print "num_binary_bytes\t"$1}\'';
#'

open(IN, "< unique_project_paths.txt");
# open(IN, "< single_project.txt");

while(<IN>) {
    chomp;
    if ($_ =~ m|^/(.*)/(.*)$|) {
        # &move_commits($1, $2);
        &collect_repo_stats($1, $2);
    }
}

close(IN);

exit(0);

sub move_commits {
    my $hacker = shift;
    my $project = shift;
    my $path = "projects/".$hacker."/".$project;
    print "mkdir -p ".$path."\n";
    print "git mv commit-logs/".$project.".txt ".$path."/commit-stat.log\n";
}

sub collect_repo_stats {
    my $hacker = shift;
    my $project = shift;
    my $path_to_repo = "/home/bob/projects/w3hn/data/github/clone/2022-04-07-run/".$project;
    open(OUT, "> projects/".$hacker."/".$project."/repo-stat.log");
    print OUT &run_cmd($hacker, $project, $cmd_num_files, $path_to_repo);
    print OUT &run_cmd($hacker, $project, $cmd_num_commits, $path_to_repo);
    print OUT &run_cmd($hacker, $project, $cmd_locs, $path_to_repo);
    print OUT &run_cmd($hacker, $project, $cmd_num_rust_files, $path_to_repo);
    print OUT &run_cmd($hacker, $project, $cmd_num_react_files, $path_to_repo);
    print OUT &run_cmd($hacker, $project, $cmd_num_markdown_files, $path_to_repo);
    print OUT &run_cmd($hacker, $project, $cmd_num_binary_files, $path_to_repo);
    print OUT &run_cmd($hacker, $project, $cmd_rust_locs, $path_to_repo);
    print OUT &run_cmd($hacker, $project, $cmd_react_locs, $path_to_repo);
    print OUT &run_cmd($hacker, $project, $cmd_markdown_locs, $path_to_repo);
    print OUT &run_cmd($hacker, $project, $cmd_binary_bytes, $path_to_repo);
    close(OUT);
}

sub run_cmd {
    my $hacker = shift;
    my $project = shift;
    my $cmd = shift;
    my $path_to_repo = shift;
    $cmd =~ s|path/to/repo|$path_to_repo|;
    print $cmd . "\n";
    my $result = `$cmd`;
    return $result;
}
