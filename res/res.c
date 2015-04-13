#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/types.h>
#include <errno.h>
#include <unistd.h>

#define FMT "%10lld"

int main(int argc, char **argv)
{
	struct rlimit rl;
	extern int errno;
	printf("cur limit :%d, max limit:%d, errno:%d\n", rl.rlim_cur, rl.rlim_max, errno);
	int ret = getrlimit(RLIMIT_FSIZE, &rl);
	if(0!=ret)
	{
		printf("system call getrlimit failed!\n");
		printf("error number is :%d\n", errno);
		printf("error info : %s\n", strerror(errno));
		exit(-1);
	}
	if(RLIM_INFINITY == rl.rlim_max)
	{
		printf("infinit!\n");
		return 0;
	}
	printf("cur limit :%d, max limit:%d\n", rl.rlim_cur, rl.rlim_max);		
	return 0;
}
