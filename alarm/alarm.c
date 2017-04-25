#include<stdio.h>
#include<stdlib.h>
#include<signal.h>

void sig_handler(int sig)
{
    printf("receive sig:%d\n", sig);
    alarm(4);
}

void main()
{
    struct sigaction act;
    act.sa_handler = sig_handler;
    act.sa_flags = 0;
    int ret = sigaction(SIGALRM, &act, NULL);
    if(ret)
    {
        printf("sigaction failed!\n");
        return;
    } 
    alarm(4);
    while(1)
    {
        sleep(1);
    }

}
