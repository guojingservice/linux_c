#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>

void sigroutine(int dunno)
{
	switch(dunno)
	{
		case SIGHUP:
			{
				printf("Receive Signal : SIGHUP\n");
			}
			break;
		case SIGINT:
			{
				printf("Receive Signal : SIGINT\n");	
			}
			break;
		case SIGQUIT:
			{
				printf("Receive Signal : SIGQUIT\n");
			}
			break;
		case SIGILL:
			{
				printf("Receive Signal : SIGILL\n");
			}
			break;
		default:
			break;
	}
	return;
}

int main()
{
	printf("my process id is :%d\n", getpid());
	signal(SIGHUP, sigroutine);
	signal(SIGINT, sigroutine);
	signal(SIGQUIT, sigroutine);
	for(;;);	
	return 0;
}

