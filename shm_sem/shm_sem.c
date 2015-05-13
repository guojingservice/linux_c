#include "share_ex.h"


#define IFLAGS (IPC_CREAT | IPC_EXCL)
#define ERR ((struct databuf *) -1)

static int shmid1, shmid2, semid;

void fatal(char *mes)
{
	perror(mes);
	exit(1);
}


// init read and write buffer
void getseg(struct databuf **p1, struct databuf **p2)
{
	// create share memory
	if((shmid1 = shmget(SHMKEY1, sizeof(struct databuf), 0600| IFLAG)) < 0)
	{
		fatal("shmget 1");
	}
	if((shmid2 = shmget(SHMKEY2, sizeof(struct databuf), 0600| IFLAG)) < 0)
	{
		fatal("shmget 1");
	}

	// attach to shared memory
	if((*p1 = (struct databuf*)(shmat(shmid1, 0, 0))) == ERR)
	{
		fatal("shmat 1");
	}
	if((*p2 = (struct databuf *)(shmat(shmid2, 0, 0))) == ERR)
	{
		fatal("shmat 2");
	}
}

// get semaphore 
int getsem()
{
	// create semaphore object
	if((semid = semget(SEMKEY, 2, 0600 | IFLAGS)) < 0)
	{
		fatal("semget");
	}
	// init semaphore object
	if((semctl(semid, 0, SETVAL, 0)) < 0)
	{
		fatal("semctl");
	}
	if((semctl(semid, 1, SETVAL, 0)) < 0)
	{
		fatal("semctl");
	}
	return (semid);
}
void remove()
{
	if(shmctl(shmid1, IPC_RMID, NULL) < 0)
	{
		fatal("shmctl1");
	}
	if(shmctl(shmid2, IPC_RMID, NULL) < 0)
	{
		fatal("shmctl2");
	}
	if(semctl(semid, IPC_RMID, NULL) <  0)
	{
		fatal("semctl");
	}
}

int main(int argc, char **argv)
{
	
	return 0;
}

