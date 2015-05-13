#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <string.h>

#define SEGSIZE 100

void usage(void)
{
	fprintf(stderr, "shmtool - A utility for tinkering with shared memory tool!\n");
	fprintf(stderr, "\nUSAGE: shmtool (w)rite <text> \n");
	fprintf(stderr, "                 (r)ead\n");
	fprintf(stderr, "                 (d)elete\n");
	fprintf(stderr, "                 (m)ode change <octal mode> \n");
	exit(1);
}

writeshm(int shmid, char *segptr, char *text)
{
	strcpy(segptr, text);
	printf("Done ... \n");
}

readshm(int shmid, char *segptr)
{
	printf("segptr:%s\n", segptr);
}

removeshm(int shmid)
{
	shmctl(shmid,IPC_RMID, 0);
	printf("Shared memory segment marked for deletion \n");
}

changemode(int shmid, char *mode)
{
	struct shmid_ds myshmds;
	// get current values for internal data structure
	shmctl(shmid, IPC_STAT, &myshmds);
	// display old permissions
	printf("old permissions were : %o\n", myshmds.shm_perm.mode);
	//convert and load the mode
	sscanf(mode , "%o", &myshmds.shm_perm.mode);
	// update the mode
	shmctl(shmid, IPC_SET, &myshmds);
	printf("New permission are : %o\n", myshmds.shm_perm.mode);
}

int main(int argc, char **argv)
{
	key_t key;
	int shmid, cntr;
	char *segptr;
	if(argc == 1)
		usage();

	// create unique key via call to ftok
	key = ftok(".", 'S');
	printf("Current Key : %x\n", key);
	//return 0;
	// open shared memory segment - create if necessary
	if((shmid = shmget(key, SEGSIZE, IPC_CREAT| IPC_EXCL|0666)) == -1)
	{
		printf("shared memory segment exists - opening as client\n");
		// segment probably already exists - try as a client
		if((shmid = shmget(key, SEGSIZE, 0)) == -1)
		{
			perror("shmget");
			exit(1);
		}
	}
	else{
		printf("Creating new shared memory segment!\n");
	}
	// attach (map) the shared memory segment into the current process
	if((segptr = shmat(shmid, 0, 0)) == (void *)-1)
	{
		perror("shmat error");
		exit(1);
	}
	switch(tolower(argv[1][0]))
	{
		case 'w':
				{
					writeshm(shmid, segptr, argv[2]);
				}
				break;
		case 'r':
				{
					readshm(shmid, segptr);
				}
				break;
		case 'd':
				{
					removeshm(shmid);
				}
				break;
		case 'm':
				{
					changemode(shmid, argv[2]);
				}
				break;
		default:
				usage();
				break;
	}
	//sleep(20);
	return 0;
}
