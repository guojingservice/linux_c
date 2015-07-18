#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>
#include <wait.h>


void pr_exit(int status)
{
	if(WIFEXITED(status))
		printf("normally termination, low-order 8 bit of exit status= %d\n", WEXITSTATUS(status));
	else if(WIFSIGNALED(status))
		printf("abnormally termination, signal number : %d\n", WTERMSIG(status));
}

int main(int argc, char **argv)
{
	pid_t pid;
	int status;
	if( (pid = fork()) < 0 )
	{
		perror("fork failed!");
		exit(-1);
	}
	else if(pid == 0)
	{
		sleep(1);
		printf("in the child process ...\n");
		exit(101);
	}
	if(wait(&status) != pid)
	{
		perror("wait failed!\n");
		exit(-2);
	}
	printf("in the parrent ...\n");
	pr_exit(status); // print status
	if((pid = fork()) < 0)
	{
		perror("fork 2 failed!");
		exit(-1);
	}
	else if(pid == 0)
	{
		abort();// generates SIGABRT
	}
	if( (wait(&status)) != pid)
	{
		perror("wait 2 faild!\n");
		exit(-2);
	}
	pr_exit(status); // print status
	
	if( (pid = fork()) <  0)
	{
		perror("fork 3 faild!");
		exit(-2);
	}
	
	else if(pid == 0)
	{
		status /= 0; // generate SIGFPE
	}
	if(wait(&status) != pid)
	{
		perror("wait 3");
		exit(-1);
	}
	pr_exit(status);
	exit(0);	
	return 0;
}
