#include "ins.h"

#define barrier() __asm__ __volatile__("":::"memory")

SingleInstance *SingleInstance::m_ins = NULL;
pthread_mutex_t SingleInstance::m_mutex = PTHREAD_MUTEX_INITIALIZER;

SingleInstance::SingleInstance()
{
   
}

SingleInstance *SingleInstance::getInstance()
{
    if(NULL == m_ins)
    {
        pthread_mutex_lock(&m_mutex);
        if (NULL == m_ins)
        {
            SingleInstance *pTemp = new SingleInstance();
            barrier(); 
            m_ins = pTemp;
        }
        pthread_mutex_unlock(&m_mutex);
    }
    return m_ins;
}
