#ifndef _SINGLE_INS_H
#define _SINGLE_INS_H
#include <pthread.h>

extern 

class SingleInstance
{
    SignleInstance *getInstance();   

private:
    SingleInstance(){ _ins = NULL;}

    SingleInstance *_ins;

};


#endif
