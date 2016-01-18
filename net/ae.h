/*
 * io多路复用 对几种机制的尝试 包括 epoll select 
 * 
 *
 */
#ifndef _AE_H
#define _AE_H
#define AE_OK 0
#define AE_ERR -1

/*
 * file event status
 */

#define AE_NONE 0
#define AE_READABLE 1
#define AE_WRITABLE 2

/*
 * timer execute flags
 */

// file event
#define AE_FILE_EVENTS 1
//time event
#define AE_TIME_EVENTS 2
//all event
#define AE_ALL_EVENTS (AE_FILE_EVENTS| AE_TIME_EVENTS)

// nonblock
#define AE_DONT_WAIT 4
// determin whether event need consisting running
#define AE_NOMORE -1

#define AE_NOTUSED(V) ((void) V)

/*
 * event processor status
 */

struct aeEventLoop;

// data structure

typedef void aeFileProc(struct aeEventLoop *eventLoop, int fd, void *clientData, int mask);

typedef int aeTimeProc(struct aeEventLoop *eventLoop, long long id, void *clientData);

typedef void aeEventFinalizerProc(struct aeEventLoop *eventLoop, void *clientData);

typedef void aeBeforeSleepProc(struct aeEventLoop *eventLoop);

/*
 * file event structure
 *
 */

typedef struct aeFileEvent{
    // listen event mask
    // the value maybe AE_READABLE or AE_WRITABLE or both of them
    int mask;

    //read event proc
    aeFileProc *rfileProc;

    //write event proc
    aeFileProc *wfileProc;

    // private data
    void *clientData;

} aeFileEvent;

/*
 * time event structure
 *
 */
typedef struct aeTimeEvent{
    //unique id of time event
    long long id;
    
    // reach point of time event
    long when_sec; // seconds
    long when_ms;   // miliseconds
    
    // handler of time event
    aeTimeProc *timeProc;
    
    // release handler of time event
    aeEventFinalizerProc *finalizerProc;

    //private data
    void *clientData;

    //point to next time event structure, formed a list
    struct aeTimeEvent *next;
    
}aeTimeEvent;

//fired event
typedef struct aeFiredEvent{
    // fired fd
    int fd;
    
    // event flask AE_READABLE or AE_WRITABLE or both
    int mask;

}aeFiredEvent;

// state of an event based program
//
typedef struct aeEventLoop{
    // max fd sofar
    int maxfd;
    
    // max number of fd tracked
    int setsize;

    // for generating max time event id
    long long timeEventNextId;
    
    // last time of execute time event
    time_t lastTime; // used to detect system clock skew

    // registered events
    aeFileEvent *events; // registered events

    // fired file evnets
    aeFiredEvent *fired;

    // time event
    aeTimeEvent *timeEventHead;

    // switch of event handler
    //
    int stop;

    // used for polling API specific data
    void *apidata;
    
    // executed before handler event
    aeBeforeSleepProc *beforesleep;

}aeEventLoop;

/* prototypes*/
aeEventLoop *aeCreateEventLoop(int setsize);

void aeDeleteEventLoop(aeEventLoop *eventLoop);

void aeStop(aeEventLoop *eventLoop);

int aeCreateFileEvent(aeEventLoop *eventLoop, int fd, int mask,
                      aeFileProc *proc, void *clientData);

void aeDeleteFileEvent(aeEventLoop *eventLoop, int fd, int mask);

int aeGetFileEvents(aeEventLoop *eventLoop, int fd);

int long long aeCreateTimeEvent(aeEventLoop *eventLoop,
                                long long milliseconds,
                                aeTimeProc *proc, void *clientData,
                                aeEventFinalizerProc *finalizerProc);

int aeDeleteTimeEvent(aeEventLoop *eventLoop, long long id);

int aeProcessEvents(aeEventLoop *eventLoop, int flags);

int aeWait(int fd, int mask, long long milliseconds);

void aeMain(aeEventLoop *eventLoop);

char *aeGetApiName(void);

void aeSetBeforeSleepProc(aeEventLoop *eventLoop, aeBeforeSleepProc beforesleep);

int aeGetSetSize(aeEventLoop *eventLoop);

int aeResizeSetSize(aeEventLoop *eventLoop, int setseize);



#endif
