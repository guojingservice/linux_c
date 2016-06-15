#ifndef _SINGLE_INS_H
#define _SINGLE_INS_H
#include <pthread.h>


class SingleInstance
{
    static SingleInstance *getInstance();   

private:
    SingleInstance();

    static SingleInstance *m_ins;
    
    static pthread_mutex_t m_mutex;
};


#endif
