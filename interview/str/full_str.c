#include<stdio.h>
#include<stdlib.h>
#include<string.h>
/*
    字符串全排列
    输入 "abc" -> acb abc bac bca cab aba
*/

// 递归
void recursion_full_str(char *str, int from, int to)
{
    if(to <= 1)
    {
        return;
    }
    if( from == to )
    {
        for(int i = 0; i < from; ++i)
        {
            printf("%c", str[i]);
        }
        printf("\n");
    }
    else
    {
        for(int i = from; i < to; ++i)
        {
            // 确定第一个
            char ch = str[from];
            str[from] = str[i];
            str[i] = ch;
            
            recursion_full_str(str, from + 1, to);
            
            //还原，保持原来的顺序
            ch = str[from];
            str[from] = str[i];
            str[i] = ch;
        }
    }
    
}

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


// 求下一个刚好比给定字符串大的字符串

void next_permutation(char *str, int len)
{
    if(len <= 0)
    {
        return;
    }
    int i = len - 1;
    char ch = str[len-1];
    while( str[i] >= ch && i >= 0)
    {
        ch = str[i--];
    }
    // already the most big
    if( i < 0 )
    {
        return;
    }
    // find the last bigger fig then str[i] 
    int j = len -1;
    while(str[j] < str[i] && j > 0)
    {
        j--;
    }
    char temp = str[i];
    str[i] = str[j];
    str[j] = temp;
    revert_str(str+i+1, len - i - 1);
    
}

int main()
{
    char temp[64];
    snprintf(temp, sizeof(temp)-1, "%s", "abcdec");
    //recursion_full_str(temp, 0, strlen(temp)); 
    next_permutation(temp, strlen(temp));
    printf("result is : [%s]\n", temp);

    return 0;
}
