#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>
#include<fcntl.h>
#include<string.h>

static int num=0;
static char namebuf[20];
static char prefix[] = "/tmp/tmp";

void int2a(int i, char *str)
{
	int power, j;
	j = i;
	for(power=1; j >= 10; j/=10)
		power *= 10;
	for(; power > 0; power /=10)
	{
		*str++ = '0' + i/power;
		i = i % power;
	}
	*str = '\0';
	return;
}

char *gentemp()
{
	int length, pid;
	// get pid
	pid = getpid();
	strcpy(namebuf, prefix);
	length = strlen(namebuf);
	int2a(pid, &namebuf[length]);
	
	strcat(namebuf, ".");
	length = strlen(namebuf);
	do{
		int2a(num++, &namebuf[length]);
	}
	while(access(namebuf, F_OK) != -1 );
	return namebuf;	
}

int main(int argc, char **argv)
{
	printf("result 1: %s\n", gentemp());
	printf("result 2: %s\n", gentemp());
	printf("result 3: %s\n", gentemp());

	return 0;
}
