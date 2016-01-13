/*
 * implement a memory pool
 * 
 *
 *
 */
#ifndef _MEMPOOL_H
#define _MEMPOOL_H
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include "util.h"

#define MEMPOOL_MAGIC 0x1234
#define MEMPOOL_BUILD 2
#define MEMPOOL_FIFO 0x00   // first in first out
#define MEMPOOL_LIFO 0x01   // last in first out


#define MEMPOOL_PAGE_SIZE 4096 // page size
#define MEMPOOL_USER_DATA_ALIGN 8 //user data align bytes


#define MEMPOOL_INVALID_INDEX -1

struct mem_block{
    int valid;
    int index;
    int prev;
    int next;
    int res;
};

#define MEMBLOCK_IS_VALID(p) ((p)->valid)

struct mem_pool{
    int magic; // check mempool
    int build; // check mempool
    int max;   // size of mempool
    int free_head;  // free list head;
    int free_tail; // free list tail
    int used_head; // used list head
    int used;       // size of used memblock
    int last_index; //last allocate index of memblock
    int inited;     // if inited
    int is_calloc; // if mempool is allocated by alloc 
    int method;     // MEMPOOL_FIFO or MEMPOOL_LIFO
    
    volatile int start; // used for check mempool_alloc and mempool_free 'satomic nature
    volatile int end;
    
    int unit;   // size of app data
    int real_unit; // after roundup size
    int size; // size of mempool
    int real_size; // real size of mempool,equals to size
    
    int block_off; // offset of memblock area
    int block_size; // size of memblock area
    
    int data_off; // offset of mem data area
    int data_size; // size of memdata area

    intptr_t last_cursor;
    intptr_t iterator_last_cursor;
    int is_iterator_reset;    

    int use_protect;
    int protect_len;
    
    char res[64]; // preserve;
    
    // start of the memblock area and data area
    struct mem_block blocks[1];

};

/*
 * some frequently used macro defined here
 *
 */

// make unit can be divisible up to round 
#define MEMPOOL_ROUND(unit, round) ( ((intptr_t)(unit) + (intptr_t)(round) -1) / (intptr_t)(round) * (intptr_t)(round) )


#define MEMPOOL_USER_DATA_UNIT_SIZE(size) MEMPOOL_ROUND(size, MEMPOOL_USER_DATA_ALIGN)

#define MEMPOOL_DATA_SIZE(max, size) (max * MEMPOOL_USER_DATA_UNIT_SIZE(size))


#define MEMPOOL_HEAD_SIZE (offsetof(struct mem_pool, blocks))

#define MEMPOOL_BLOCK_SIZE(max) (max * sizeof(struct mem_block)) 

#define MEMPOOL_INNER_DATA_BASE_SIZE(max) (MEMPOOL_HEAD_SIZE + MEMPOOL_BLOCK_SIZE(max))

//alia to page size of linux
#define MEMPOOL_INNER_DATA_SIZE(max) MEMPOOL_ROUND(MEMPOOL_INNER_DATA_BASE_SIZE(max),MEMPOOL_PAGE_SIZE)

// total size of mempool
#define MEMPOOL_CALC(max, unit) (MEMPOOL_INNER_DATA_SIZE(max) + MEMPOOL_DATA_SIZE(max, unit))


#define MEMPOOL_GET_PTR(pstpool, idx) ((struct mem_block *)((pstpool)->blocks + ((size_t)(idx) % (pstpool->max)))) 


#define MEMPOOL_IDX2POS(pm, idx) ((idx) % (pm)->max)

#define MEMPOOL_INSERT_FREE_LINK_HEAD(pmempool, pblock) {   \
    int pos = MEMPOOL_IDX2POS(pmempool, (pblock)->index);   \
    (pmempool)->next = (pmempool)->free_head;               \
    (pmempool)->valid = 0;                                  \
    (pmempool)->prev = MEMPOOL_INVALID_INDEX;               \
    if(MEMPOOL_INVALID_INDEX == (pmempool)->free_head){     \
        (pmempool)->free_tail = pos;                        \
    }else{                                                   \
        typeof(*pblock) *pnext = MEMPOOL_GET_PTR(pmempool, (pmempool)->free_head);                                                          \
        pnext->prev = pos;                                     \
    }                                                           \
    (pmempool)->free_head = pos;                            \
}

#define MEMPOOL_INSERT_FREE_LINK_TAIL(pmempool, pblock) {\
    (pblock)->next = MEMPOOL_INVALID_INDEX;             \
    (pblock)->valid = 0;                                \
    if(MEMPOOL_INVALID_INDEX == (pmempool)->free_tail){ \
        (pmempool)->free_head = MEMPOOL_IDX2POS(pmempool, (pblock)->index); \
        (pmempool)->free_tail = (pmempool)->free_head;  \
        (pblock)->prev = MEMPOOL_INVALID_INDEX;         \
    }else{                                              \
        typeof(*pblock) *ptail = MEMPOOL_GET_PTR(pmempool, (pmempool)->free_tail);               \
        ptail->next = MEMPOOL_IDX2POS(pmempool, (pblock)->index);               \
        (pmempool)->free_tail = ptail->next;                                   \
        (pblock)->prev = MEMPOOL_IDX2POS(pmempool,(ptail)->index);              \
    }\
}

#define MEMPOOL_GET_DATA(pmempool, pblock)      ({\
    int pos = MEMPOOL_IDX2POS(pmempool,(pblock)->index);    \
    (void *)((size_t)(pmempool) + (pmempool)->data_off + (pmempool)->real_unit * pos);                           \
})


#define MEMPOOL_DELETE_FREE_LINK(pmempool, pblock) {\
    (pmempool)->free_head = (pblock)->next;\
    if(MEMPOOL_INVALID_INDEX == (pmempool)->free_head){ \
        (pmempool)->free_tail = MEMPOOL_INVALID_INDEX; \
    }else{ \
        typeof(*pblock) *phead = MEMPOOL_GET_PTR(pmempool, (pmempool->free_head));\
        phead->prev = MEMPOOL_INVALID_INDEX;\
    }  \
}

#define MEMPOOL_DELETE_USED_LINK(pmempool, pblock)  {       \
    (pblock)->valid = 0;                                    \
    if(MEMPOOL_INVALID_INDEX != (pblock)->prev){            \
        typeof(*pblock) pprev = MEMPOOL_GET_PTR(pmempool, (pblock)->prev); \
        pprev->next = (pblock)->next;                       \
    }else{                                                  \
        pmempool->used_head = (pblock)->next;    \
    }                                                                   \
    if(MEMPOOL_INVALID_INDEX != (pblock)->next){             \
        typeof(*pblock) pnext = MEMPOOL_GET_PTR(pmempool, (pblock)->next); \
        pnext->prev = (pblock)->prev;        \
    }                                                               \
}

#define MEMPOOL_INSERT_USED_LINK(pmempool, pblock) {\
    if(MEMPOOL_INVALID_INDEX != (pmempool)->used_head){\
        typeof(*pblock) *pnext = MEMPOOL_GET_PTR(pmempool, (pmempool)->used_head);\
        pnext->prev = MEMPOOL_IDX2POS(pmempool, (pblock)->index);\
    }\
    (pblock)->next = (pmempool)->used_head; \
    (pblock)->prev = MEMPOOL_INVALID_INDEX; \
    (pmempool)->used_head = MEMPOOL_IDX2POS(pmempool, (pblock)->index);\
    (pmempool)->used ++; \
    (pblock)->valid = 1; \
}
// calculate the size of mem needed by mempool
/*
 * @ max: capacity of mempool
 * @ unit: size of app data
 * @ return: the size of memory required by mempool
 */

unsigned int __mempool_calc_size(unsigned int max, unsigned int unit);


// init mempool memory, form free list
/*
 * @ppmempool: pp of mempool
 * @max: capacity of mempool
 * @unit: size of app data
 * @pbase: base pointer of mempool
 * @size: size of pbase point to
 *
 * @return: 0 success 
 *          -1 fail
 */
int mempool_init(struct mem_pool **ppmempool, unsigned int max, 
                 unsigned int unit,
                 void *pbase,
                 unsigned int size);


void __mempool_init_head(struct mem_pool *pmempool,
                         unsigned int max,
                         unsigned int unit,
                         unsigned int size);

void __mempool_init_body(struct mem_pool *pmempool);

int __mempool_check_head(struct mem_pool *pmempool,
                         unsigned int max,
                         unsigned int unit,
                         unsigned int size);

int __mempool_check_chain(struct mem_pool *pmempool);


/* allocate mempool memory and init
 *
 * @ppmempool: pp to mempool
 * @max: capacity of mempool
 * @unit: size of app data
 *
 * @return: 0 success
 *          -1 fail
 */ 
int mempool_new(struct mem_pool **ppmempool,
                unsigned int max,
                unsigned int unit);


// TODO
// attach a existed memory,check the data
// mempool_attach
//


/* destroy mempool created by mempool_new
 *
 * @ppmempool: pp to mempool
 *
 * @return: 0 success
 *          -1 fail
 *
 */
int mempool_destroy(struct mem_pool **ppmempool);


/*
 * set method of the mempool, FIFO or LIFO
 *
 * @pmempool: pointer to mempool
 * @method: integer of method
 *
 * @return: -1:failed 
 *          old method: success
 */

static inline int mempool_set_method(struct mem_pool *pmempool, 
                                     int method){
    int old;
    if(NULL == pmempool)
        return -1;
    
    old = pmempool->method;
    pmempool->method = method;
    return old;
}

/*
 * allocate one memblock and return the idx
 *
 * @pmempool: pointer to mempool
 *
 * @return: idx of the allocated memblock
 *
 */

int mempool_alloc(struct mem_pool *pmempool);


/*
 * get the address of the allocated memory by idx
 * 
 * @pmempool: pointer to mempool
 * @idx: idx allocated by mempool
 *
 * @return: the address of the allocated for app data
 */
void * mempool_get(struct mem_pool *pmempool, int idx);


#endif
