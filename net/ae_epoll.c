#include <sys/epoll.h>

//event status
typedef struct aeApiState{
    // epoll event
    int epfd;
    // event bucket
    struct epoll_event *events;
    
}aeApiState;

// create a new epoll instance , and asign it to eventLoop

static int aeApiCreate(aeEventLoop *eventLoop){
    aeApiState *state = (aeApiState*)malloc(sizeof(*state));
    if(!state)
        return -1;
    
    // init event buckets space
    state->events = (struct epoll_event*)malloc(sizeof(struct epoll_event)*eventLoop->setsize);
    
    if(!state->events){
        free(state);
        state=NULL;
        return -1;
    }
    
    state->epfd = epoll_create(1024);

    if(state->epfd == -1){
        free(state->events);
        free(state);
        return -1;
    }
    eventLoop->apidata = state;    
}

// resize
//
static int aeApiResize(aeEventLoop *eventLoop, int setsize){
    aeApiState *state = eventLoop->apidata;
    state->events = (struct epoll_event*)realloc(state->events, sizeof(struct epoll_event)*setsize);
    return 0;
}

// free epoll instance and buckets

static int aeApiFree(aeEventLoop *eventLoop){
    aeApiState *state = eventLoop->apidata;
    
    close(state->epfd);
    free(state->events);
    free(state);
}

// add new event to fd
static int aeApiAddEvent(aeEventLoop *eventLoop, int fd, int mask){
    aeApiState *state = eventLoop->apidata;
    
    struct epoll_event ee;
    // if fd already monitored for some event, then a MOD op needed
    // otherwize an ADD op needed
    int op = eventLoop->events[fd].mask == AE_NONE ?
                EPOLL_CTL_ADD : EPOLL_CTL_MOD;

    //register event to epoll
    ee.events = 0;
    mask |= eventLoop->events[fd].mask;
    
    if(mask & AE_READABLE) ee.events |= EPOLLIN;
    if(mask & AE_WRITABLE) ee.events |= EPOLLOUT;

    ee.data.u64 = 0; // avoid valgrind warning
    ee.data.fd = fd;
    
    if(epoll_ctl(state->epfd, op, fd, &ee) == -1) return -1;
    
    return 0;
}

// delete event from fd
static void aeApiDelEvent(aeEventLoop *eventLoop, int fd, int delmask){
    aeApiState *state = eventLoop->apidata;
    struct epoll_event ee;
    
    int mask = eventLoop->events[fd].mask & (~delmask);
    
    ee.events = 0;
    if(mask & AE_READABLE) ee.events |= EPOLLIN;
    if(mask & AE_WRITABLE) ee.events |= EPOLLOUT;
    
    ee.data.u64 = 0;
    ee.data.fd = fd;
    if(mask != AE_NONE){
        epoll_ctl(state->epfd, EPOLL_CTL_MOD, fd, &ee);
    }else{
        epoll_ctl(state->epfd, EPOLL_CTL_DEL, fd, &ee);
    }
}

// obtain executable events
static int aeApiPoll(aeEventLoop *eventLoop, struct timeval *tvp){
    aeApiState *state = eventLoop->apidata;
    
    int retval, numevents = 0;
    
    // waite time
    retval = epoll_wait(state->epfd, state->events, eventLoop->setsize,
                tvp ? (tvp->tv_sec * 1000 + tvp->tv_usec/1000) : -1;
    
    if (retval > 0){
        int j;
        // set mod for fired event and add it to eventLoop 's fired events
        numevents = retval;
        for(j =0; j < numevents; ++j)
        {
            int mask  = 0;
            struct epoll_event *e = state->events + j;
            if(e->events & EPOLLIN) mask |= AE_READABLE;
            if(e->events & EPOLLOUT) mask |= AE_WRITABLE;
            if(e->events & EPOLLERR) mask |= AE_WRITABLE;
            if(e->events & EPOLLHUP) mask |= AE_WRITABLE;
    
            eventLoop->fired[i].fd = e->data.fd;
            eventLoop->fired[i].mask = mask;

        }
        
    }
    return numevents;
}

// give a name
static char *aeApiName(void){
    return "epoll";
}
