#include <stdio.h>
#include <sys/time.h>
#include <sys/types.h>
#include <stdlib.h>
#include <poll.h>
#include <string.h>
#include <time.h>
#include <errno.h>

#include "ae.h"

#ifdef HAVE_EPOLL
#include "ae_epoll.c"
#else
    #include "ae_select.c"
#endif

// init event handler status
aeEventLoop *aeCreateEventLoop(int setsize){
    aeEventLoop *eventLoop = NULL;
    int i;
    
    do{
        if((eventLoop = (aeEventLoop*)malloc(sizeof(*eventLoop))) == NULL )
            break;
        memset(eventLoop, 0, sizeof(*eventLoop));
        // init file event structure and fired event structure array
        eventLoop->events = (aeFileEvent*)(malloc(sizeof(aeFileEvent)*setsize));
        eventLoop->fired = (aeFiredEvent*)malloc(sizeof(aeFiredEvent)*setsize);
        if(eventLoop->events == NULL || NULL == eventLoop->fired)
            break;
        //set array size
        eventLoop->setsize = setsize;
        // set recent exe time
        eventLoop->lastTime = time(NULL);
        
        // init time event stucture
        eventLoop->timeEventHead = NULL;
        eventLoop->timeEventNextId = 0;
        eventLoop->stop = 0;
        eventLoop->maxfd = -1;
        eventLoop->beforesleep = NULL;
        
        if(aeApiCreate(eventLoop) == -1)
            break;

        // init listen events
        for(i=0; i < setsize; ++i){
            eventLoop->events[i].mask = AE_NONE;
        }
        return eventLoop;
    }while(0);
    
    if(eventLoop){
        if(eventLoop->events){
            free(eventLoop->events);
            eventLoop->events = NULL;
        }
        if(eventLoop->fired){
            free(eventLoop->fired);
            eventLoop->fired = NULL;
        }
        free(eventLoop);
    }
 
    return NULL;
}

//return the current set size

int aeGetSetSize(aeEventLoop *eventLoop){
    return eventLoop->setsize;
}


// reset the maximum set size of the event loop

int aeResizeSetSize(aeEventLoop *eventLoop, int setsize){
    int i; 
    if(setsize == eventLoop->setsize) return AE_OK;
    if(eventLoop->maxfd >= setsize) return AE_ERR;
    if((aeApiResize(eventLoop, setsize)) == -1) return AE_ERR;

    eventLoop->events = (aeFileEvent*)realloc(eventLoop->events, sizeof(aeFileEvent)*setsize);
    eventLoop->fired = (aeFiredEvent*)realloc(eventLoop->fired, sizeof(aeFiredEvent)*setsize);
    eventLoop->setsize = setsize;

    // init new slots
    for(i = eventLoop->maxfd +1; i < setsize; ++i){
        eventLoop->events[i].mask = AE_NONE;
    }
    return AE_OK;    
}


// delete event handler
void aeDeleteEventLoop(aeEventLoop *eventLoop){
    aeApiFree(eventLoop);
    free(eventLoop->events);
    free(eventLoop->fired);
    free(eventLoop);
}

