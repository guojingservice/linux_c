#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/mman.h>
#include <fcntl.h>


int roundUp(int input, int base)
{
    if(input <= 0) return base;
    return (input / base) * base +  (input % base == 0 ? 0: 1 ) * base;
}

void main()
{
    char * fileName = "./tdata.mmap";
    int lastError = 0;
    int pageSize = getpagesize();
    struct stat statBuf;
    int ret = stat(fileName, &statBuf);
    if(ret != 0 )
    {
        printf("stat file :[%s] failed. errno:[%d]\n",
                fileName, errno);
        lastError = errno;
        char *errMsg = strerror(errno);
        printf("ErrorMsg:[%s]\n", errMsg);
        return;
    }
    
    printf("file size:[%d], pageSize:[%d]\n", 
            statBuf.st_size, pageSize);

    int roundSize = roundUp(statBuf.st_size, pageSize);
    printf("begin resize to :[%d]\n", roundSize);
    ret = truncate(fileName, roundSize);
    if(ret != 0)
    {
        printf("truncate failed!, errno:%d", errno);
        return;
    }
    int fd = open(fileName, O_RDWR);
    void * ptr = mmap(NULL, roundSize, PROT_READ|PROT_WRITE, MAP_SHARED,
            fd, 0);
    if(ptr == MAP_FAILED)
    {
        printf("mmap failed!");
        return;
    }
    char temp[] = "hello, world!";
    memcpy(ptr, temp, sizeof(temp) - 1);
    ret = munmap(ptr, roundSize);
    if(ret != 0)
    {
        printf("munmap failed!");
        return;
    }
    
}
