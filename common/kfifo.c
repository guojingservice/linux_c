#include "kfifo.h"


// this method implicit make sure the fifo list woun't exceed
// meanwhile, if the queue is nearly full, not all data will be put into it
// in this case, i think maybe usr's program need handle this situation 
// themself
unsigned int __kfifo_put(struct kfifo *fifo,
                                       const unsigned char *buffer,
                                       unsigned int len){
    unsigned int k;
    len = min(len, fifo->size - fifo->in + fifo->out);
    // put data starting from in to buffer end if needed
    k = min(len, fifo->size - (fifo->in & (fifo->size -1)));
    memcpy(fifo->buffer + (fifo->in & (fifo->size-1)), buffer, k);
    
    // then put the rest if needed
    memcpy(fifo->buffer, buffer + k, len - k);
    fifo->in += len;
    return len;
}
/*
 * the same princaple to reach this gaol
 *
 *
 */
unsigned int __kfifo_get(struct kfifo *fifo,
                                       unsigned char * buffer,
                                       unsigned int len){
    unsigned int k;
    len = min(len, fifo->in - fifo->out);
    
    k = min(len, fifo->size - (fifo->out &(fifo->size -1 )));

    memcpy(buffer, fifo->buffer + (fifo->out & (fifo->size-1)), k);
    
    memcpy(buffer + k, fifo->buffer, len - k);
    
    
    fifo->out += len;
    
    return len;
}

/*
 * peek sth in the queue
 *
 */
unsigned int __kfifo_peek(struct kfifo *fifo,
                          unsigned char *buffer,
                          unsigned int len){
    unsigned int k;
    len = min(len, fifo->in - fifo->out);
    k = min(len, fifo->size - (fifo->out & (fifo->size - 1)));
    memcpy(buffer, fifo->buffer + (fifo->out &(fifo->size-1)), k);
    memcpy(buffer+k, fifo->buffer, len-k);
    return len;
}


struct kfifo *kfifo_init(unsigned char *buffer,
                         unsigned int size
                                       ){
    struct kfifo *fifo;
    /* size should bea power of 2
     *      * so that kfifo->in % kfifo->size can be replaced with kfifo->in &(kfifo->size-1) with a faster speed
     */
    assert(is_power_of_2(size));
    fifo = malloc(sizeof(struct kfifo));
    if(!fifo)
        return NULL;
    fifo->buffer = buffer;
    fifo->size = size;
    fifo->in = fifo->out = 0;

    if( 0 != pthread_mutex_init(&fifo->mutex, NULL))
    {
        free(fifo);
        fifo = NULL;
        printf("pthread_mutex_init failed!");
        return NULL;
    }
    return fifo;
}

struct kfifo *kfifo_alloc(unsigned int size)
{
    unsigned char *buffer;
    struct kfifo *ret;
    if(!is_power_of_2(size)){
        printf("WARNING : size is not power of 2!");
        size = roundup_power_of_2(size);
    }
    buffer = malloc(size);
    if(!buffer){
        printf("error: malloc failed!");
        return NULL;
    }
    ret = kfifo_init(buffer, size);
    if(!ret){
        printf("error: kfifo_init failed!\n");
        free(buffer);
        buffer = NULL;
        return NULL;
    }
    return ret;
}

