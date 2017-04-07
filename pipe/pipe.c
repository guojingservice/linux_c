#include<stdio.h>
#include<stdlib.h>
#include<string.h>

int main()
{
    FILE *read_fp;
    char buf[1024 + 1];
    int chars_read;
    memset(buf, '\0', sizeof(buf));
    read_fp = popen("uname -a", "r");
    if(read_fp != NULL)
    {
        chars_read = fread(buf, sizeof(char), sizeof(buf)-1, read_fp);
        if(chars_read > 0)
        {
            printf("Output:\n%s\n", buf);
        }
        pclose(read_fp);
        return 0;
    } 
    return 0;
}
