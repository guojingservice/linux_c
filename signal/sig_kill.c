#include<stdio.h>
#include<stdlib.h>
#include <signal.h>

int ntimes = 0;

void p_action(int dunno)
{
	printf("Parrent caught signal [%d]\n", ++ntimes);
}

void c_action(int dunno)
{
	printf("Child caught signal [%d]\n", ++ntimes);	
}

int main()
{
	int p_action();
	void (*pf_action)(int) = NULL;
	
	signal(SIGUSR1, p_action);
	pid_t pid;
	
	switch(pid = fork())
	{
		case -1:
			perror("fork failed!");
			exit(1);
		case 0:
			// set child process SIGUSR1
			signal(SIGUSR1, c_action);
			// get parent pid
			pid_t ppid = getppid();
			for(;;)
			{
				sleep(1);
				kill(ppid, SIGUSR1);
				pause();
			}
			break;
		default:
			for(;;)
			{
				pause();
				sleep();
				kill(pid, SIGUSR1);	
			}
		
	}
	
	return 0;
}
