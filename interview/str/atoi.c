#include<stdio.h>
#include<stdlib.h>
#include<ctype.h>
int str_to_int(const char *str, int len)
{
    static const int MAX_INT = (int) ((unsigned)~0 >> 1);
    static const int MIN_INT = -(int)(~0 >> 1) - 1;
    int c;
    int n;
    if(len <=0 )
    {
        return 0;
    }
    
    int i = 0;
    while( i < len && str[i] == ' ')
    {
        i++;
    }
    if(i >= len)
    {
        return 0;
    }
    int sign = 1;
    if( str[i] == '+' || str[i] == '-')
    {
        if(str[i] == '-')
        {
            sign = -1;
        }
        i++;
    }
    if( i >= len)
    {
        return 0;
    }
    while(isdigit(str[i]))
    {
        c = str[i] - '0';
        if(sign > 0 && ((n > MAX_INT / 10) || ( n == MAX_INT / 10 && c > MAX_INT % 10)))
        {
            n  = MAX_INT;
            break;
        }
        else if(sign < 0 &&( ( n < MIN_INT / 10) ||(n == MIN_INT && c > MIN_INT % 10)))
        {
            n = MIN_INT;
            break;
        }
        n =  n * 10 + c;

    }
    
    return sign > 0 ? n : -n;
}

int main()
{
    return 0;
}
