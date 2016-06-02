/*
    字符串包含 子集 

*/


#include<stdio.h>
#include<stdlib.h>
#include<string.h>


// 蛮力轮询

int str_contain(char * str1, int len1, char * str2, int len2)
{
    int i,j;
    int find = 0;
    for(i =0; i < len2; i++)
    {
        for( j = 0; j < len1; j++)
        {
            if( *(str2 + i) == *( str1 + j))
            {
               break; 
            }
        }
        if( j >= len1)
        {
            find = 1;
        }
    }
    
    if(find != 0)
    {
        return 1;
    }
    return 0;
    
}
//位运算

int str_contain_bit(char *str1, int len1, char *str2, int len2)
{
    long mapbit = 0;
    int i = 0;
    for( i =0; i < len1; ++i)
    {
        mapbit = mapbit | (1 << (str1[i] - 'A'));    
    }
    for (i = 0; i < len2; ++i)
    {
        if( ((1 << (str2[i] - 'A')) & mapbit) == 0)
        {
            return 1;
        }
    }
    return 0;
} 


void test()
{
    char temp1[128];
    char temp2[128];
    snprintf(temp1, sizeof(temp1)-1,  "%s", "FABCDDGREGRNBRW");
    snprintf(temp2, sizeof(temp2)-1,  "%s", "BADFGRBN");
    //printf("%d\n", str_contain(temp1, strlen(temp1), temp2, strlen(temp2)));
    printf("%d\n", str_contain_bit(temp1, strlen(temp1), temp2, strlen(temp2)));
    
}
//97 122 65 90
int main()
{
    //printf("%d %d %d %d long:%lu\n", 'a','z','A','Z',sizeof(long long));
    test();
    
    return 0;
}
