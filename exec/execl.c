#include<stdio.h>
#include<unistd.h>

int main()
{
	printf("Preparing to Executing ls\n");
	execl("/bin/ls", "ls", "-al", NULL); // attention, here need a NULL endpoint
	// if execl returned, then that means execl called failed
	perror("failed to execute ls!");
	return 0;
}
