/*
 * 字符串 翻转
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

// O(n)
void rotate_str(char *pStr, int len, char c)
{
    char *pStart = pStr;
    char *pCur = pStr;
    while(pCur <= pStr + len && pStart <= pStr + len)
    {
        if( *pCur == c || pCur == pStr + len )
        {
            revert_str(pStart, pCur - pStart);
            pStart = pCur + 1;
            pCur = pStart +1;
        }
        else
        {
            pCur += 1;
        }
    }
    
    revert_str(pStr, len); 
}

void test()
{
    char temp[128];

    // test revert
    /* 
    snprintf(temp, sizeof(temp)-1, "aaa hello, world!");
    snprintf(temp, sizeof(temp)-1, "ab");
    printf("before: %s\n", temp);
    revert_str(temp, strlen(temp));    
    printf("after: %s\n", temp);
    */
    
    snprintf(temp, sizeof(temp) - 1, "I am a student.");
    printf("before : %s\n", temp); 
    rotate_str(temp, strlen(temp), ' ');  
    printf("after : %s\n", temp);
    
}

int main()
{
    test();
    return 0;
}
