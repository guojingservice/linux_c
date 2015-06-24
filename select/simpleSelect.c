#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/time.h>
#include <unistd.h>

#define STDIN 0

int main(int argc, char **argv)
{
	struct timeval tv;
	fd_set readfds;

	// set timeout 2 seconds
	tv.tv_sec = 2;
	tv.tv_usec = 500000;

	FD_ZERO(&readfds);
	FD_SET(STDIN, &readfds);

	select(STDIN + 1, &readfds, NULL, NULL, &tv);

	if(FD_ISSET(STDIN, &readfds))
	{
		// true
		printf("A key was pressed!\n");
	}
	else
	{
		printf("time out !\n");	
	}
	return 0;
}
