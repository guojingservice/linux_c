#ifndef _COM_TEST_H
#define _COM_TEST_H

#include <stdio.h>
#include <stdlib.h>
#include "dlist.h"


void comTestList()
{
    list *pList = listCreate();
    if(pList)
        printf("list create success!\n");
    
    int a[5] = {1,2,3,4,5};
    int i = 0;
    for(i=0;i<sizeof(a)/sizeof(a[0]);++i) 
    {
        listAddNodeTail(pList, &a[i]);
    }
    
    listIter *iter = listGetIterator(pList, S_HEAD_TO_TAIL);
    listNode *node;
    printf("value of the list : \n");
    while((node = listNext(iter))!= NULL)
    {
        printf(" %p ", node->value);
    }
    printf("\n");
    printf("count of the list : %d\n", listLength(pList));
    printf("head value of the list : %p\n", pList->head->value);
    printf("tail value of the list : %p\n", pList->tail->value);
}



#endif
