/*
 * mmap a fifo into a file and remap it from a file
 *
 *
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
//#include "../common/"

struct Stu{
    int a;
    char c;
    char name[32];
};

void saveToFile(const struct Stu *pStu){
   
     
}
void loadFromFile(struct Stu *pStu){

}

int main()
{
    struct Stu per;
    per.a = 5;
    per.c ='p';
    strncpy(per.name, "guojing",sizeof(per.name)-1);
    
    saveToFile(&per);
        
    return 0;
}
