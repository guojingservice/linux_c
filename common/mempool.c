#include "mempool.h"


unsigned int __mempool_calc_size(unsigned int max, unsigned int unit){
    unsigned int size;
    size = MEMPOOL_CALC(max, unit);
    return size;
}

int mempool_init(struct mem_pool **ppmempool,
                 unsigned int max,
                 unsigned int unit,
                 void *pbase,
                 unsigned int size){
    

}

void __mempool_init_head(struct mem_pool *pmempool,
                         unsigned int max,
                         unsigned int unit,
                         unsigned int size){
    int i;
    char *padding;
    
    assert(NULL != pmempool);
    
    pmempool->magic = MEMPOOL_MAGIC;
    pmempool->build = MEMPOOL_BUILD; 
    
    pmempool->max = max;
    pmempool->unit = unit;
    pmempool->real_unit = MEMPOOL_USER_DATA_UNIT_SIZE(unit);
    
    pmempool->size = MEMPOOL_CALC(max, unit);
    pmempool->real_size = size;
    
    pmempool->used = 0;


    pmempool->start = 0;
    pmempool->end = 0;


    pmempool->free_head = -1;
    pmempool->free_tail = -1;

    pmempool->used_head = -1;
    
    pmempool->last_cursor = -1L;
    pmempool->iterator_last_cursor = -1L;
    pmempool->is_iterator_reset = 0;
    
    pmempool->method = MEMPOOL_FIFO;
    
    pmempool->block_off = offsetof(struct mem_pool, blocks);
    pmempool->block_size = MEMPOOL_BLOCK_SIZE(max);
    
    pmempool->data_off = MEMPOOL_INNER_DATA_SIZE(max);
    pmempool->data_size = MEMPOOL_DATA_SIZE(max, unit);
    
    pmempool->use_protect = 0;
    pmempool->protect_len = MEMPOOL_INNER_DATA_SIZE(max);

    
    padding = (char *) pmempool + MEMPOOL_INNER_DATA_BASE_SIZE(max);

    for( i = 0; i < (pmempool->data_off - MEMPOOL_INNER_DATA_BASE_SIZE(max)); ++i){
        *padding++ = i;
    }
    
    return;
}

void __mempool_init_body(struct mem_pool *pmempool){
    struct mem_block *ptail;
    struct mem_block *pblock;
    
    assert( NULL != pmempool);
    
    int i;
    
    if(pmempool->max <= 0 )
        return;
    
    pmempool->free_head = 0;
    pmempool->free_tail = 0;

    ptail = MEMPOOL_GET_PTR(pmempool, pmempool->free_tail);

    ptail->next = -1;
    ptail->valid = 0;
    memset(&ptail->res, 0, sizeof(ptail->res));
    ptail->index = 0;
    ptail->prev = -1;

    for( i = 1; i < pmempool->max; ++i){
        ptail = MEMPOOL_GET_PTR(pmempool, pmempool->free_tail);
        pblock = MEMPOOL_GET_PTR(pmempool, i);
    
        pblock->valid = 0;
        memset(&pblock->res, 0, sizeof(pblock->res);
        pblock->index = 0;
        pblock->next = -1;
        pblock->prev = i - 1;
        ptail->next = i;
        pmempool->free_tail = i;
    } 
    return;

}

int mempool_new(struct mem_pool **ppmempool,
                unsigned int max, unsigned int unit){
    unsigned int size = 0;
    if( (0 >= max) || (0 >= unit))
        return -1;
    
    size = MEMPOOL_CALC(max, unit);
    
    if(size / unit < max)
        return -1;


    if(!ppmempool)
        return size;
    //calloc will set every bit to 0
    *ppmempool = (struct mem_pool *) calloc(1, size);
    
    if(!*ppmempool)
        return -1;

    // init head
    __mempool_init_head(*ppmempool, max, unit, size); 

    // init body
    __mempool_init_body(*ppmempool);    

    (*ppmempool)->is_calloc = 1;
    (*ppmempool)->inited = 1;

    return 0;

}


