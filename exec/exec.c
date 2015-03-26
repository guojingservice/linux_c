#include<stdio.h>
#include<unistd.h>

int main()
{
	printf("Preparing to Executing ls\n");
	execl("/bin/ls", "ls", "-al", NULL);
	// if execl returned, then that means execl called failed
	perror("failed to execute ls!");
	return 0;
}
