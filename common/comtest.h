#ifndef _COM_TEST_H
#define _COM_TEST_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "dlist.h"
#include "klist.h"

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

void comTestKlist()
{
    typedef struct stu{
        char name[64];
        int num;
        struct list_head list;
    }Stu;
    
    static LIST_HEAD(stu_list); // init list head
    char *stuNames[5] = {"Tom", "Kattom", "Tony", "Matheral","Ted"};
    int i;
    for( i = 0; i < sizeof(stuNames)/sizeof(stuNames[0]); ++i)
    {
        // init node
        Stu *pNew = malloc(sizeof(struct stu));
        if(!pNew)
            exit(1);
        sprintf(pNew->name,"%s", stuNames[i]);
        pNew->num = i;
         
        list_add_tail(&pNew->list, &stu_list);
    }
    
    
    // iterat list, use list_for_each
    struct list_head *cur;
    Stu *pStu = NULL;
    /*
    list_for_each(cur, &stu_list)
    {
        pStu = list_entry(cur, Stu, list);     
        printf("Name :%s, Num:%d, Stu Address:%p\n", 
                pStu->name, 
                pStu->num,
                pStu);
    }
    */

    // iterate list, use list_for_each_entry
    list_for_each_entry(pStu, &stu_list, list)
    {
        printf("Name :%s, Num:%d, Stu Address:%p, NodeAddress:%p\n",
                pStu->name,
                pStu->num,
                pStu,
                &pStu->list);
    }
    printf("head prev:%p, head next:%p\n", pStu->list.prev, pStu->list.next);// still can access the invlid member address
    printf("End pStu :%p, Danger Name:%s, DangerNum:%d\n", 
            pStu,
            pStu->name,
            pStu->num);
    //free(pStu); this will cause invalid member address access
    //
    
    
     
}




#endif
