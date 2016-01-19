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

// get object fd 's event
int aeGetFileEvents(aeEventLoop *eventLoop, int fd){
    if(fd >= eventLoop->setsize) return 0;
    aeFileEvent *fe = &eventLoop->events[fd];
    return fe->mask;
}

// get current time of seconds and milliseconds 
static void aeGetTime(long *seconds, long *milliseconds){
    struct timeval tv;
    gettimeofday(&tv, NULL);
    *seconds = tv.tv_sec;
    *milliseconds = tv.tv_usec/1000;
}

// make current time added by given milliseconds
// and save result to sec and ms
static void aeAddMillisecondsToNow(long long milliseconds, long *sec, long *ms){
    long cur_sec, cur_ms, when_sec, when_ms;
    // get current time
    aeGetTime(&cur_sec,&cur_ms);
    
    // calc result of after added milliseconds 
    
    when_sec = cur_sec + milliseconds/1000;
    when_ms = cur_ms + millisecons%1000;
    
    if(when_ms >=1000)
    {
        when_sec++;
        when_ms -= 1000;
    }
    
    *sec = when_sec;
    *ms = when_ms;
}

// creat time event
//
long long aeCreateTimeEvent(aeEventLoop *eventLoop, long long milliseconds,
                            aeTimeProc *proc, void *clientData,
                            aeEventFinalizerProc *finalizerProc){
    // update time calc counter
    long long id = eventLoop->timeEventNextId ++;
    // create time event structure
    aeTimeEvent *te;
    te = (aeTimeEvent*)malloc(sizeof(*te));
    if(NULL == te) return AE_ERR;
    
    // set id
    te->id = id;
    
    // set handler of time event
    aeAddMillisecondsToNow(milliseconds, &te->when_sec, &te->when_ms);
    
    // set event hander
    te->timeProc = proc;
    te->finalizerProc = finalizerProc;
    
    // set private data
    te->clientData = clientData;

    // put new event to the heand of the list
    te->next = eventLoop->timeEventHead;
    eventLoop->timeEventHead = te;

    return id;
}

// delete object id of time event
int aeDeleteTimeEvent(aeEventLoop *eventLoop, long long id)
{
    aeTimeEvent *te, *prev=NULL;
    //foreach the list
    te = eventLoop->timeEventHead;
    
    while(te){
        if(te->id == id_
        {
            if(prev == NULL)
                eventLoop->timeEventHead = te->next;
            else
                prev->next = te->next;
            // exe clear func
            if(te->finalizerProc)
                te->finalizerProc(eventLoop, te->clientData);
            
            free(te);
            
            return AE_OK;
        }
    }
    return AE_ERR;
}

// search the first timer to fire

/* optimizations:
 *  1) insert the event in order, so that the nearest is just the head
 *      still, insertion or deletion is O(N)
 *  2) use a skiplist to have the op as O(1), insertion as O(log(N))
 *
 */

static aeTimeEvent *aeSearchNearestTimer(aeEventLoop *eventLoop){
    aeTimeEvent *te = eventLoop->timeEventHead;
    aeTimeEvent *nearest = NULL;
    
    while(te){
        if(!nearest || te->when_sec < nearest->when_sec ||
            (te->when_sec == nearest->when_sec && te->when_ms < nearest->when_ms))
            nearest = te;
        te = te->next;
    }
    return nearest;
}

//process all time events

static int processTimeEvents(aeEventLoop *eventLoop){
    int processed = 0;
    aeTimeEvent *te;
    long long maxId;
    time_t now = time(NULL);
    //reset lasttime in case of chaos
    if( now < eventLoop->lastTime){
        te = eventLoop->timeEventHead;
        while(te){
            te->when_sec = 0;
            te = te->next;
        }
    }    
    
    // update lastTIme
    eventLoop->lastTime = now;
    
    // foreach time event list 
    // process time event handler
    te = eventLoop->timeEventHead;
    maxId = eventLoop->timeEventNextId - 1;
    while(te){
        long now_sec, now_ms;
        long long id;
        // skip invalid events
        // in fact, id which is greater then maxId may be add in the 
        // time event handler process, to avoid loop forever,wo need this
        // maxID to help us to control our range in a limit
        if(te->id > maxId){
            te = te->next;
            continue;
        }
        
        // get current time
        aeGetTime(&now_sec, &now_ms);
        // if now greater or equals to event exe time, then execute it
        if(now_sec > te->when_sec ||
           (now_sec == te->when_sec && now_ms >= te->when_ms)){
            int retval;
            id = te->id;
            retval = te->timeProc(eventLoop, id, te->clientData);
            processed++;

            // record if to cycle this time event
            if(retval != AE_NOMORE){
                aeAddMillisecondsToNow(retval, &te->when_sec, &te->when_ms);            }else{
                aeDeleteTimeEvent(eventLoop, id);
            }
            
            // time event list may be changed after some event is executed
            te = eventLoop->timeEventHead;


            }
        }else{
            te = te->next;
        }
    }
    return processed;
}

//process event depending on flags parameter
int aeProcessEvents(aeEventLoop *eventLoop, int flags){
    int processed = 0, numevents;
    // nothing to to
    if(!(flags&AE_TIME_EVENTS) && !(flags & AE_FILE_EVENTS))
        return 0;
    
    if(eventLoop->maxfd != -1 ||
        ((flags & AE_TIME_EVENTS) && !(flags & AE_DONT_WAIT))){
        int j;
        aeTimeEvent *shortest = NULL;
        struct timeval tv, *tvp;
        // get recent time event
        if(flags & AE_TIME_EVENTS &&
            !(flags & AE_DONT_WAIT))
            shortest = aeSearchNearestTimer(eventLoop);
        if(shortest){
            // calc the tmie missing for the nearest
            aeGetTime(&now_sec, &now_ms);
            tvp = &tv;
            tvp->tv_sec = shortest->when-sec - now_sec;
            if(shortest->when_ms < now_ms){
                tvp->tv_usec = ((shortest->when_ms+1000) - now_ms)*1000;
                tvp->tv_sec --;

            }else{
                tvp->tv_usec = (shortest->when_ms- now_ms)*1000;
            }
            if(tvp->tv_sec < 0) tvp->tv_sec = 0;
            if(tvp->tv_usec < 0) tvp->tv_usec= 0;
            
        }
    }else{
        // there is no time event
        // depend on FLAG, decided to whether block
        if(flags & AE_DONT_WAIT){
            tv.tv_sec = tv.tv_usec = 0;
            tvp = &tv;
        }
        else{
            tvp = NULL;
        }
    }
    
    // handle file event, block time is depended on tvp
    numevents = aeApiPoll(eventLoop, tvp);
    for(j = 0; j < numevents; ++j){
        //pick up fired event
        aeFileEvent *fe = &eventLoop->events[eventLoop->fired[j].fd];
        int mask = eventLoop->fired[j].mask;
        int fd = eventLoop->fired[j].fd;
        int rfired = 0;
        
        if(fe->mask & mask & AE_READABLE){
        // ifired is to make sure only one of read or write event will be executed
            rfired = 1;
            fe->rfileProc(eventLoop, fd, fe->clientData, mask);
        }
        if(fe->mask & mask & AE_WRITABLE){
            if(!rfired || fe->wfileProc != fe->rfileProc)
                fe->wfileProc(eventLoop, fd, fe->clientData, mask);
        }
        processed++;
    }
    // check time events
    if(flags & AE_TIME_EVENTS)
        processed += processTimeEvents(eventLoop);
    return processed;

}


// wait for fd become readable , writable or exception occured
int aeWait(int fd, int mask, long long milliseconds){
    struct pollfd pfd;
    int retmask = 0; retval;
    memset(&pfd, 0, sizeof(pfd));
    
    pfd.fd = fd;
    if(mask & AE_READABLE)pfd.events |= POLLIN;
    if(mask & AE_WRITABLE)pfd.events |= POLLOUT;
    if((retval = poll(&pfd, 1, milliseconds)) == 1){
        if(pfd.revents & POLLIN) retmask |= AE_READABLE;
        if(pfd.revents & POLLOUT) retmask |= AE_WRITABLE;
        if(pfd.revents & POLLERR) retmask |= AE_WRITABLE;
        if(pfd.revents & POLLHUP) retmask |= AE_WRITABLE;
        return retmask;
    }
    else{
        return retval;
    }
}

// main loop of event handler
void aeMain(aeEventLoop *eventLoop){
    eventLoop->stop = 0;
    while(!eventLoop->stop){
        // if there is sth needed executed before event process,then do it
        if(eventLoop->beforesleep != NULL){
            eventLoop->beforesleep(eventLoop);
        }
        // start event process
        aeProcessEvents(eventLoop, AE_ALL_EVENTS);
    }
}

// return the name 
char *aeGetApiName(void){
    return aeApiName();
}

// set hander needed do before event handler
void aeSetBeforeSleepProc(aeEventLoop *eventLoop, aeBeforeSleepProc *beforesleep){
    eventLoop->beforesleep = beforesleep;
}
