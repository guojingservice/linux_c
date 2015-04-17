#include<stdio.h>
#include <stdlib.h>

#include <sys/types.h>
#include <signal.h>
#include <unistd.h>
#include <syslog.h>

void daemon_init(const char *pname, int facility)
{
	int i;
	pid_t pid;
	pid = fork();
	if(pid < 0)
	{
		perror("fork failed!");
		exit(1);
	}
	if(pid > 0)
	{
		exit(0);
	}
	setsid();
	
	signal(SIGHUP, SIG_IGN);
	// fork and end the first child process
	if((pid = fork()) < 0)
	{
		perror("first child process fork failed!");
		exit(1);
	}
	if(pid > 0)
	{
		exit(0);
	}
	// the second child process
	int daemon_proc = 1;
	// change work dir to '/'
	chdir("/");
	// unmask file fd
	umask(0);
	// close all file descripter
	// TODO ...
	openlog(pname, LOG_PID, facility);
	sleep(60);
}

int main()
{
	daemon_init("test_dp", 0);
	return 0;
}
