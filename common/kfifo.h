#ifndef _KFIFO_H
#define _KFIFO_H

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <assert.h>
#include <string.h>
#include "util.h"
/*
 * thread safe fifo queue implementation
 *
 */

struct kfifo{
    unsigned char *buffer; // buffer to save data
    unsigned int size;     // buffer size
    unsigned int in;       // in delta
    unsigned int out;      // out delta
    pthread_mutex_t mutex; // mutex
};

struct kfifo *kfifo_init(unsigned char *buffer, unsigned int size);
struct kfifo *kfifo_alloc(unsigned size);


static inline void kfifo_free(struct kfifo *fifo){
    if(fifo){
        if(fifo->buffer)
            free(fifo->buffer);
        pthread_mutex_destroy(&fifo->mutex); 
        free(fifo);
    }
}

static inline void __kfifo_reset(struct kfifo *fifo){
    fifo->in = fifo->out = 0;
}

unsigned int __kfifo_put(struct kfifo *fifo,
                               const unsigned char *buffer,
                               unsigned int len);
unsigned int __kfifo_get(struct kfifo *fifo,
                               unsigned char * buffer,
                               unsigned int len);

unsigned int __kfifo_peek(struct kfifo *fifo,
                          unsigned char *buffer,
                          unsigned int len);

static inline void kfifo_reset(struct kfifo *fifo){
    pthread_mutex_lock(&fifo->mutex);
    __kfifo_reset(fifo);
    pthread_mutex_unlock(&fifo->mutex);
}

static inline unsigned int kiffo_peek(struct kfifo *fifo,
                                      unsigned char *buffer,
                                      unsigned int len)
{
    unsigned int ret;
    pthread_mutex_lock(&fifo->mutex);
    ret = __kfifo_peek(fifo, buffer, len);
    pthread_mutex_unlock(&fifo->mutex);
    return ret;
}

static inline unsigned int kfifo_get(struct kfifo *fifo,
                                     unsigned char *buffer,
                                     unsigned int len)
{
    unsigned int ret;
    pthread_mutex_lock(&fifo->mutex);
    ret = __kfifo_get(fifo, buffer, len);
    if(fifo->in == fifo->out)
        fifo->in = fifo->out = 0;
    pthread_mutex_unlock(&fifo->mutex); 
    return ret;
}

static inline unsigned int kfifo_put(struct kfifo *fifo,
                                     unsigned char *buffer,
                                     unsigned int len)
{
    unsigned int ret;
    pthread_mutex_lock(&fifo->mutex);
    ret = __kfifo_put(fifo, buffer, len);
    pthread_mutex_unlock(&fifo->mutex);
    return ret;
}   

static inline unsigned int __kfifo_len(struct kfifo *fifo){
    return fifo->in - fifo->out;
}

static inline unsigned int kfifo_len(struct kfifo *fifo){
    unsigned int ret;
    pthread_mutex_lock(&fifo->mutex);
    ret = __kfifo_len(fifo);
    pthread_mutex_unlock(&fifo->mutex);
    return ret;
}

static inline unsigned int __kfifo_available_size(struct kfifo *fifo){
    return fifo->size - fifo->in + fifo->out;
}

static inline unsigned int kfifo_available_size(struct kfifo *fifo){
    unsigned int ret;
    pthread_mutex_lock(&fifo->mutex);
    ret = __kfifo_available_size(fifo);
    pthread_mutex_unlock(&fifo->mutex);
    return ret;
}



#endif
