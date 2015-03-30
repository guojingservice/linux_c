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
		sleep(2);
		exit(1);
	}
	// parent process
	if(wait(&status) < 0)
	{
		perror("parent wait failed!");
		exit(1);
	}
	// check the returned value
	printf("value of status : %d\n", status);
	printf("WIFEXITED(status) : %d\n", WIFEXITED(status));
	if(!WIFEXITED(status))
	{
		printf("child process exit abnomally! macro:%d, exit : %d", WIFEXITED(status), WEXITSTATUS(status));
		exit(1);
	}
	printf("child process exit normally!\n");
	
	exit(0);	
	return 0;
}
