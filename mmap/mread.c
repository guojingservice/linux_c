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

void load_from_mdata(const char *fileName)
{
    struct stat statBuf;
    int ret = stat(fileName, &statBuf);
    if(ret != 0)
    {
        printf("stat failed!");
        return;
    }
    int fileSize = statBuf.st_size;
    int fd = open(fileName, O_RDWR);
    if(fd < 0 )
    {
        printf("open file :[%s] failed!\n", fileName);
        return;
    }
    void * ptr = mmap(NULL, fileSize, PROT_READ|PROT_WRITE, MAP_SHARED,
            fd, 0);
    if(ptr == MAP_FAILED)
    {
        printf("mmap failed!");
        return;
    }
    char temp[1024] = {0};
    int mapLen;
    memcpy(&mapLen, ptr, sizeof(mapLen));
    memcpy(temp, ptr + sizeof(mapLen), mapLen);
    temp[mapLen] = 0;
    printf("mapLen:[%d], data:[%s]\n", mapLen, temp);
}

void main()
{
    load_from_mdata("./tdata.mmap");
}
