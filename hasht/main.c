#include <stdio.h>
#include <stdlib.h>
#include "strmap.h"

int main(int argc, char **argv)
{
	StrMap *sm = sm_new(10);
	int iRet = sm_put( sm, "bill", "rescued");
	if( 1 == iRet )
	{
		printf("StrMap input bill success!\n");
	}
	iRet = sm_put( sm, "thomas", "not rescued");
	if( 1 == iRet )
	{
		printf("StrMap input thomas success!\n");
	}
	printf("now strmap count is %d\n", sm_get_count(sm));

	printf("bill exists result is :%d\n", sm_exists(sm, "bill"));
	return 0;
}
