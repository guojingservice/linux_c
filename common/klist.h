#ifndef _K_LIST_H
#define _K_LIST_H

#include "util.h"

/*
 *
 *  linux kernel double linked cycled list implementation
 *  most list asumes that a head entry is involved
 */


// just used for init a structure
#define LIST_HEAD_INIT(name) { &(name), &(name) }

#define LIST_HEAD(name) \
    struct list_head name = LIST_HEAD_INIT(name)


//LIST_HEAD(new_list)
//
//struct list_head new_list = { &(name), &(name)}
//


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


/*
 * used by our self
 */ 
static inline void __list_add(struct list_head *new, 
                              struct list_head *prev,
                              struct list_head *next)
{
    next->prev = new;
    new->next = next;
    new->prev = prev;
    prev->next = new;
}

/*
 * list del 
 */
static inline void __list_del(struct list_head *prev,
                              struct list_head *next)
{
    prev->next = next;
    next->prev = prev;
}

/*
 * list splice
 *
 */
static inline void __list_splice(struct list_head *list,
                                 struct list_head *prev,
                                 struct list_head *next)
{
    struct list_head *first = list->next;
    struct list_head *last = list->prev;
    
    first->prev = prev;
    prev->next = first;

    next->prev = last;
    last->next = next;
     
}

/*
 * add new entry
 * @new: new entry
 * @head: list head to add it after
 *
 */ 
static inline void list_add(struct list_head *new, struct list_head *head)
{
    __list_add(new, head, head->next);
}

/*
 * add new entry to tail
 * @new: new entry to be add
 * @head: list head to add it before
 *
 */
static inline void list_add_tail(struct list_head *new, struct list_head *head)
{
    __list_add(new, head->prev, head);
}

/*
 * delete a entry
 * @entry: entry to delete
 *
 */
static inline void list_del(struct list_head *entry)
{
    __list_del(entry);
    // entry->prev = LIST_POISON1 ?? 0x00100100 + POISON_POINTER_DELTA
    // entry->next = LIST_POISON2 ?? 0x00100100 ...
}


/*
 * delete entry from list and reinitialize it
 * @entry: the element to delete from
 *
 */
static inline void list_del_init(struct list_head *entry)
{
    __list_del(entry->prev, entry->next);
    INIT_LIST_HEAD(entry);
}

/*
 * check if the list is empty
 *
 * @head: the head to check
 */
static inline int list_empty(const struct list_head *head)
{
    return head->next == head;
}


/*
 * move an entry from one list to another
 * @list: list to move from
 * @head: list entry to move to after
 *
 */
static inline void list_move(struct list_head *list, struct list_head *head){
    __list_del(list->prev, list->next);
    __list_add(list, head, head->next);
}

/*
 * splice two list
 * @list: list to insert from
 * @head: list to intert after
 *
 */
static inline void list_splice(struct list_head *list, struct list_head *head)
{
    if(!list_empty(list))
        __list_splice(list, head, head->next);
}
static inline void list_splice_init(struct list_head *list,
                                    struct list_head *head)
{
    if(!list_empty(list))
    {
        __list_splice(list, head, head->next);
        INIT_LIST_HEAD(list);
    }
}

#endif
