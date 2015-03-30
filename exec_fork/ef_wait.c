#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>


int main(int argc, char **argv)
{
	int pid, status, exit_status;
	if((pid = fork())<0)
	{
		perror("fork failed!");
		exit(1);
	}	
	// child process
	if(!pid)
	{
		sleep(5);
		exit(5);
	}
	// parent process
	if(wait(&status) < 0)
	{
		perror("parent wait failed!");
		exit(1);
	}
	
	
	
	return 0;
}
