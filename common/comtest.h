#ifndef _COM_TEST_H
#define _COM_TEST_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "dlist.h"
#include "klist.h"
#include "kfifo.h"

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

// global shared fifo
struct kfifo *pkfifo = NULL;
int needFinish = 0;
// put int into fifo
void *thr_put(void *arg){
    int i;
    int ret;
    printf("put thread start!\n");
    for(i=0;i<10000000;++i){
        ret = kfifo_put(pkfifo, (unsigned char *)&i, sizeof(i));
        if(ret != sizeof(i)){
            if(kfifo_len(pkfifo) == pkfifo->size)
            {
                    printf("fifo is full, sleep 1 second!\n");
                    sleep(1);
            }
            else
            {
                printf("put failed!\n");
                break;    
            }
        }
        printf("put %d\n", i);
        //sleep 1
        //sleep(1);
    }
    needFinish = 1;// end the get thread
}

// get int from fifo
void *thr_get(void *arg){
    int ret;
    int data;
    printf("get thread start!\n");
    while(1){
        ret = kfifo_get(pkfifo, (unsigned char *)&data, sizeof(data));
        if(ret == sizeof(data))
            printf("get %d\n",data);
        if(needFinish&&kfifo_len(pkfifo)==0)
            break;
    }
}

// kfifo test
void comTestFifo(){
    // allocate  a fifo
    pkfifo = kfifo_alloc(1 << 20);
    /*
    int a[2] = {2,4};
    kfifo_put(pkfifo, (unsigned char *)(&a[0]), sizeof(a[0]));
    kfifo_put(pkfifo, (unsigned char *)(&a[1]), sizeof(a[0]));

    while(kfifo_len(pkfifo)>0){
        int data;
        kfifo_get(pkfifo, (unsigned char *)&data, sizeof(data));
        printf("get : %d\n", data);   
    } 
    */

    
    // then create two thread, one put int into fifo, one read int from fifo
    pthread_t ptid, gtid;
    
    int err = pthread_create(&ptid, NULL, thr_put, NULL);
    if(0!= err){
        printf("put thread create failed!\n");
        return ;  
    }
    err = pthread_create(&gtid, NULL, thr_get, NULL);
    if(0!=err){
        printf("get thread create failed!\n");
        return ;
    }
    int *ret;
    pthread_join(ptid, (void **)&ret);
    printf("put thread returned!\n");
    pthread_join(gtid, (void **)&ret);
    printf("get thread returned!\n");
    kfifo_free(pkfifo);
    return ;
}



#endif
