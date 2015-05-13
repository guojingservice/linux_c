#include <stdio.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/sem.h>


// share memory key
#define SHMKEY1_t (key_t)0x10
#define SHMKEY2_T (key_t)0x15

// key of semaphore

#define SEMKEY (key_t)0x20


// read and write buf size

#define SIZ 5*BUFSIZ

struct databuf{
	int d_nread;
	char d_buf[SIZ];
};


