#include<stdio.h>
#include<sys/types.h>
#include<sys/stat.h>

int main()
{
	mode_t new_umask, old_umask;
        new_umask = 0666;
        old_umask = umask(new_umask);
        printf("original mask : %o\n", old_umask);
        printf("new mask : %o\n", new_umask);
        system("touch testSample");
        printf("created file testSample\n");
        new_umask = 0444;
        old_umask = umask(new_umask);
        printf("original mask : %o\n", old_umask);
        printf("new umask : %o\n", new_umask);
        system("touch testSample2");
        printf("created new file testSample2\n");
        system("ls -l testSample testSample2");
        return 0;
}
