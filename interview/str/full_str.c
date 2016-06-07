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


int main()
{
    char temp[64];
    snprintf(temp, sizeof(temp)-1, "%s", "abcd");
    recursion_full_str(temp, 0, strlen(temp)); 
    return 0;
}
