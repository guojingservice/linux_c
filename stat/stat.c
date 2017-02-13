#include<stdio.h>
#include<sys/stat.h>
#include<sys/types.h>
#include<errno.h>
#include<fcntl.h>
#include<string.h>
#include<unistd.h>

void adapt_file(const char* filename)
{
    struct stat fsbuf;
    int ret = stat(filename, &fsbuf);
    int cperror = 0;
    if( 0 != ret)
    {
        cperror = errno;
        printf("stat failed! error:%d, msg:%s\n", cperror, strerror(cperror));
    }
    if(cperror != ENOENT)
    {
        printf("stat success! size:%d\n", fsbuf.st_size);
        return;
    }
    printf("prepare to create a empty file!\n");
    
    int fd = open(filename, O_CREAT, 0666);
    if( fd < 0)
    {
        printf("create file failed!\n");
        return;
    }
    
    ret = truncate(filename, 24);
    if( 0 !=  ret)
    {
        cperror = errno;
        printf("truncate failed! error:%d, msg:%s\n", cperror, strerror(cperror));
        return;
    }
    
    ret = stat(filename, &fsbuf);
    if( 0 != ret)
    {
        printf("stat failed! truncate failed to create a file");
        return;
    }
    printf("trucnate file:%s success, size:%d\n", filename, fsbuf.st_size);
}

int main()
{
    adapt_file("./data.st");
	return 0;
}
