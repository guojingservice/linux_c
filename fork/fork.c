#include <stdio.h>
#include <unistd.h>
int main()
{
	
	printf("Befor Fork..\n");
	
	pid_t pid = fork();
	if(pid < 0)
	{
		printf("error occured when call fork()\n");
	}
	if(pid == 0 )
	{
		printf("I am the child\n");
	}
	else if(pid > 0)
	{
		printf("I am the parent!\n");
	}
	return 0;
}
