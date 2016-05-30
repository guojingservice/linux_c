/*
 * 字符串翻转 1 蛮力翻转
 */
#include<stdio.h>
#include<stdlib.h>
#include<string.h>


// O(n)
void revert_str(char *pStr, int n)
{
    if( n <= 1)
    {
        return;
    }
    int i = 0;
    char ch = 0;
    for( i = 0; i < n / 2; ++i)
    {
        ch = *(pStr + i);
        *(pStr + i) = *(pStr + (n - i -1));
        *(pStr + (n - i - 1)) = ch;
    }
    
}

int main()
{
    char temp[128];
    snprintf(temp, sizeof(temp)-1, "aaa hello, world!");
//    snprintf(temp, sizeof(temp)-1, "ab");
    printf("before: %s\n", temp);
    
    revert_str(temp, strlen(temp));    
    printf("after: %s\n", temp);
    return 0;
}
