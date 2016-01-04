#include <stdio.h>

#include "comtest.h"

int main()
{
    /*
    int a = -1;
    //unsigned int b = (unsigned int)a;
    //printf("b is %u\n",b);
    unsigned int c = 1 << 31;
    unsigned int d = c - 1;
    printf("c=%u\nd=%u\nc-d=%u\n", c,d,c-d);
    unsigned int m = c+d;
    unsigned int n = m +1;
    unsigned int k = m + 4;

    printf("m=%u\nn=m+1=%u\nk=m+4=%u\n", m,n,k);
    printf("k-m=%u\n",k-m);

    unsigned short m1 = 1 << 15;
    unsigned short m2 = m1 -1;
    unsigned short m3 = m1 + m2;
    unsigned short k1 = m3 +1, k2 = m3+4;
    printf("k1=m3+1=%u\nk2=m3+4=%u\n", k1, k2);
    unsigned short k3 = k2 - m3;
    printf("k3 = k2-m3=%u\n", k3);
    return 0;
    */
    //comTestList(); 
    //comTestKlist();     
    comTestFifo();
    return 0;   
}
