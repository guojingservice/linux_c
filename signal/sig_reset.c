#include<stdio.h>
#include<stdlib.h>
#include <signal.h>
// process is running a signal process function when receive a same signal, the process will 
// continue running, the new signal will be saved untill the last signal function is completed
// and the appropriate signal process function will be executed


void interrupt(int dunno)
{
	printf("Interrupt called!\n");
	printf("sleep 4 seconds ...\n");
	sleep(4);
	printf("Interrupt Function Ended\n");
}

int main()
{
	int t_now = time(NULL);
	printf("Start Time : %d\n", t_now);
	signal(SIGINT, interrupt);
	printf("Interrupt set for SIGINT\n");
	sleep(10);
	printf("Program NORMAL ended.\n");
	t_now = time(NULL);
	printf("End Time : %d\n", t_now);
	return 0;
}
