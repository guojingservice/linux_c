#ifndef _K_LIST_H
#define _K_LIST_H

#include "util.h"

/*
 *
 *  linux kernel double linked cycled list implementation
 *
 */

struct list_head{
    struct list_head *next, *prev;
};

/*
 * init list_head
 */
static inline INIT_LIST_HEAD(struct list_head *list)
{
    list->next = list;
    list->prev = list;
}

static inline void __list_add(struct list_head *new, 
                              struct list_head *prev,
                              struct list_head *next)
{
    next->prev = new;
    new->next = next;
    new->prev = prev;
    prev->next = new;
}




#endif
