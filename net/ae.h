/*
 * io多路复用 对几种机制的尝试 包括 epoll select 
 * 
 *
 */

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
typedef struct 
