#include<stdio.h>
#include<string.h>

int main()
{
    int i;
    for(i = 0; i< 256; ++i)
    {
        printf("errno:%d, errorMsg:%s\n", i, strerror(i));   
    }
    return 0;
}

