#include <stdlib.h>
#include "dlist.h"

list *listCreate(void)
{
    struct list *list;
    if((list = (struct list *)malloc(sizeof(*list))) == NULL)
        return NULL;
    list->head = list->tail = NULL;
    list->len = 0;
    list->dup = NULL;
    list->free = NULL;
    list->match = NULL;
    return list;
}

void listRelease(list *list)
{
    unsigned long len;
    struct listNode *current, *next;
    len = list->len;
    current = list->head;
    while(len--)
    {
        next = current->next;
        if(list->free) list->free(current->value);
        free(current);
        current = next;
    }
    free(list);
}

list *listAddNodeHead(list *list, void *value)
{
    struct listNode *node;
    if((node = (listNode *)malloc(sizeof(*node))) == NULL)
        return NULL;
    node->value = value;
    if(list->len == 0)
    {
        list->head = list->tail = node;
        node->prev = node->next = NULL;    
    }
    else
    {
        node->prev = NULL;
        node->next = list->head;
        list->head->prev = node;
        list->head = node;
    }
    list->len++;
    return list;
}

list *listAddNodeTail(list *list, void *value)
{
    struct listNode *node;
    if((node = (struct listNode *)malloc(sizeof(*node))) == NULL)
        return NULL;
    node->value = value;
    if(list->len == 0 )
    {
        list->head = list->tail = node;
        node->prev = NULL;
        node->next = NULL;
    }
    else
    {
        list->tail->next = node;
        node->prev = list->tail;
        node->next = NULL;
        list->tail = node;
    }
    list->len++;
    return list;
}
    
list *listInsertNode(list *list, listNode *old_node,void *value, int after)
{
    struct listNode *node;
    if((node = (struct listNode *)malloc(sizeof(*node))) == NULL)
        return NULL;
    node->value = value;
    if(after)
    {
        node->next = old_node->next;
        node->prev = old_node;
        old_node->next = node;
        if(node->next)
            node->next->prev = node;
        if(list->tail == old_node)
            list->tail = node;
    }
    else
    {
        node->next = old_node;
        node->prev = old_node->prev;
        old_node->prev = node;
        if(node->prev)
            node->prev->next = node;
        if(list->head == old_node)
            list->head = node;
    }
    list->len++;
    return list;
}
void listDelNode(list *list, listNode *node)
{
    if(node->prev)
        node->prev->next = node->next;
    else
        list->head = node->next;
    if(node->next)
        node->next->prev = node->prev;
    else
        list->tail = node->prev;
    if(list->free)
        list->free(node->value);
    free(node);
    list->len--;    
}

listIter *listGetIterator(list *list, int direction)
{
    listIter *iter;
    if((iter = malloc(sizeof(*iter)))==NULL) return NULL;
    if( direction == S_HEAD_TO_TAIL )
    {
        iter->next = list->head;
    }
    else
    {
        iter->next = list->tail;
    }
    iter->direction = direction;
    return iter;    
}
listNode *listNext(listIter *iter)
{
    listNode *current = iter->next;
    
    if( NULL != current )
    {
        if(iter->direction == S_HEAD_TO_TAIL)
        {
            iter->next = current->next;
        }
        else
        {
            iter->next = current->prev;
        }
    }
    return current;
}

void listReleaseIterator(listIter *iter)
{
    free(iter);
}
/*
 * duplicate the list without modifing the original list
 * if the dup method of the list is not set, then just copy the node value
        return NULL;
 */
list *listDup(list *orig)
{
    struct list *newList;
    listIter *iter;
    listNode *node;
   
    if((newList = listCreate()) == NULL)
        return NULL;
    newList->dup = orig->dup;
    newList->free = orig->free;
    newList->match = orig->match;
    iter = listGetIterator(orig, S_HEAD_TO_TAIL);
    while((node = listNext(iter))!=NULL)
    {
        void *value;
        if(newList->dup)
        {
            value = newList->dup(node->value);
            if(NULL == value)
            {
                listRelease(newList);
                listReleaseIterator(iter);
                return NULL;
            }
        }
        else
        {
            value = node->value;    
        }
        if(listAddNodeTail(newList, value) == NULL)
        {
            listRelease(newList);
            listReleaseIterator(iter);
            return NULL;
        }
    }
    listReleaseIterator(iter);
    return newList;
}

listNode *listSearchKey(list *list, void *key)
{
    listIter *iter;
    listNode *node;
    
    iter = listGetIterator(list, S_HEAD_TO_TAIL);
    while((node = listNext(iter)) != NULL)
    {
        if(list->match)
        {
            if(list->match(node->value, key)){
                listReleaseIterator(iter);
                return node;
            }
        }
        else
        {
            if(key == node->value){
                listReleaseIterator(iter);
                return node;
            }
        }
    }
    listReleaseIterator(iter);
    return NULL;
}


listNode *listIndex(list *list, long index){
    listNode *node;
    if(index < 0){
        index = (-index) -1;
        node = list->tail;
        while(index-- && node ) node = node->prev;
    }
    else{
        node = list->head;
        while(index-- && node) node = node->next;
    }
    return node;
}

void listRewind(list *list, listIter *li){
    li->next = list->head;
    li->direction = S_HEAD_TO_TAIL;    
}
void listRewindTail(list *list, listIter *li){
    li->next = list->tail;
    li->direction = S_TAIL_TO_HEAD;
}

/*
 * rotate the list
 */

void listRotate(list *list){
    
    listNode *tail = list->tail;
    if(listLength(list) <= 1) return;
    
    list->tail = tail->prev;
    list->tail->next = NULL;
    
    list->head->prev = tail;
    tail->prev = NULL;
    tail->next = list->head;
    list->head = tail;
}

