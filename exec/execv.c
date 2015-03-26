#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
int main()
{
	char *av[] = {"ls", "-l", NULL};
	execv("/bin/ls", av);
	// if this method returned,then error occured when calling ls
	perror("execv failed");	
	exit(1);
	return 0;
}
