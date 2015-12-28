#ifndef _KFIFO_H
#define _KFIFO_H

#include <pthread.h>


struct kfifo{
    unsigned char *buffer; // buffer to save data
    unsigned int size;     // buffer size
    unsigned int in;       // in delta
    unsigned int out;      // out delta
    pthread_mutex_t mutex; // mutex
};



#endif
