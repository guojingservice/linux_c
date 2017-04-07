#include<stdio.h>
#include<stdlib.h>
#include<string.h>

int main()
{
    FILE *write_fp;
    char buf[1024 + 1];
    snprintf(buf, sizeof(buf)-1, "%s", "once you got the job done...");
    int chars_read;
    write_fp = popen("od -Ax", "w");
    if(write_fp != NULL)
    {
        chars_read = fwrite(buf, sizeof(char), strlen(buf), write_fp);
        pclose(write_fp);
        return 0;
    } 
    return 0;
}
