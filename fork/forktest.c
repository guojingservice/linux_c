#include <stdio.h>
#include <unistd.h>
int main()
{
    int i =0;
    for(i = 0; i < 4; ++i)
    {
        pid_t pid = fork();
        if(pid == 0)
        {
            printf("new child!\n");        
        }
    }	
	return 0;
}
