#include <stdio.h>
#include <stdlib.h>
#include <sys/ipc.h>
#include <sys/types.h>
#include <sys/sem.h>
#include <ctype.h>
#include <semaphore.h>


#define SEM_RESOURCE_MAX  1 // initial value of all semaphores


// you should define this union yourself, or compiler will not find this structure
union semun
{
	int val;
	struct semid_ds *buf;
	unsigned short int *array;
	struct seminfo *__buf;
};


unsigned short get_member_count(int sid);

void dispval( int sid, int member);

// get value of one semaphore 
int get_sem_val( int sid, int semnum )
{
	return ( semctl( sid, semnum, GETVAL, 0) );
}


// init semaphore

void init_semaphore( int sid, int semnum, int initval )
{
	union semun semopts;
	semopts.val = initval;
	semctl( sid, semnum, SETVAL, semopts );
}

// get mode information
void getmode( int sid )
{
	int rc;
	union semun semopts;
	struct semid_ds mysemds;
	//struct semid_ds mysemds;
	// allocate memory for buf
	semopts.buf = &mysemds;
	if(( rc = semctl(sid, 0, IPC_STAT, semopts)) == -1)
	{
		perror("semctl");
		exit(1);
	}
	printf("Permission Mode were %o\n", semopts.buf->sem_perm.mode);
	return;
}

void opensem(int *sid, key_t key)
{
	// open the semaphore set = do not create
	if((*sid = semget(key, 0, 0666)) == -1)
	{
		perror("Semaphore set does not exist!");
		exit(1);
	}
}

void createsem(int *sid, key_t key, int members)
{
	int cntr;
	union semun semopts;
	// here i don't know how to get parameter of max members yet
	// temperarily write like this 
	if( members > 250 )
	{
		fprintf(stderr, "max number of semaphore in a set is %d\n", 250);
		exit(1);
	}
	printf("creating new semaphore set with %d members\n", members);
	if((*sid = semget(key, members, IPC_CREAT | IPC_EXCL | 0666)) == -1 )
	{
		perror("create new semaphore set failed!, maybe it already exists\n");
		exit(1);
	}	
	semopts.val = SEM_RESOURCE_MAX;
	// initialize all members (could be done by SETALL)
	for( cntr = 0; cntr < members; ++cntr)
	{
		semctl( *sid, cntr, SETVAL, semopts );
	}
	printf("init success. initial value %d\n", SEM_RESOURCE_MAX);
}

void locksem( int sid, int member )
{
	struct sembuf sem_lock = {0, -1, IPC_NOWAIT};
	if( member < 0 || member > (get_member_count(sid) -1))
	{
		fprintf(stderr, "semaphore member %d out of range!\n");
		return;
	}
	// attempt to lock the semaphore set
	if(!getval(sid, member))
	{
		perror("Semaphore resources exhautsted!");
		exit(1);
	}

	sem_lock.sem_num = member;
	if((semop(sid, &sem_lock, 1)) == -1)
	{
		perror("lock failed!");
		exit(1);
	}
	printf("Semaphore resources decremented by one(locked)\n");
	dispval( sid, member );
}

void unlocksem( int sid, int member )
{
	struct sembuf sem_unlock = { member, 1, IPC_NOWAIT};
	int semval;
	if( member < 0 || member > (get_member_count(sid) -1) )
	{
		fprintf(stderr, "semaphore member %d out of range!\n", member);
		return;
	}
	// check if already locked
	semval = getval(sid, member);
	if(semval == SEM_RESOURCE_MAX )
	{
		fprintf(stderr, "Semaphore not locked!\n");
		exit(1);
	}
	sem_unlock.sem_num = member;
	// attempt to lock semaphore set
	if( semop( sid, &sem_unlock, 1) == -1 )
	{
		fprintf(stderr, "unlock failed\n");
		exit(1);
	}
	printf("Semaphore resources incremented by one(unlock)");
	dispval( sid, member );
}

void removesem( int sid )
{
	semctl( sid, 0, IPC_RMID, 0 );
	printf("Semaphore removed \n");
}

unsigned short get_member_count(int sid)
{
	union semun semopts;
	struct semid_ds mysemds;

	semopts.buf = &mysemds;

	// return number of members in the semaphore set
	return (semopts.buf->sem_nsems);
}

int getval( int sid, int member )
{
	int semval;
	semval = semctl( sid, member, GETVAL, 0 );
	return (semval);
}

void changemode( int sid, char *mode)
{
	int rc;
	union semun semopts;
	struct semid_ds mysemds;
	// get current values for internal data structure
	semopts.buf = &mysemds;

	rc = semctl( sid, 0, IPC_STAT, semopts);
	if( rc == -1)
	{
		perror("semctl");
		exit(1);
	}
	printf("Old permissions were %o\n", semopts.buf->sem_perm.mode);
	// change permission on the semaphore 
	sscanf(mode, "%ho", &semopts.buf->sem_perm.mode);
	// update the internal data structure
	semctl(sid, 0, IPC_SET, semopts);
	printf("Updated mode ...\n");

}

void dispval( int sid, int member)
{
	int semval;
	semval = semctl( sid, member, GETVAL, 0 );
	printf("semval for member :%d is %d\n", member, semval);
}

void usage(void)
{
	fprintf(stderr, "semtool - A utility for tinkering with semaphores\n");
	fprintf(stderr, "\nUSAGE: semtool4 (c)reate <semcout>\n");
	fprintf(stderr, "                  (l)ock <sem #>\n");
	fprintf(stderr, "                  (u)nlock <sem #>\n");
	fprintf(stderr, "                  (d)elete\n");
	fprintf(stderr, "                  (m)ode <mode>\n");
	exit(1);
}

int main(int argc, char **argv)
{
	key_t key;
	int semset_id;
	if(argc == 1)
		usage();
	// create unique key via call to ftok()
	key = ftok(".", 's');
	switch(tolower(argv[1][0]))
	{
		case 'c': 
				{
					if(argc != 3)
						usage();
					createsem(&semset_id, key, atoi(argv[2]));
				}
				break;
		case 'l':
				{
					if(argc != 3)
						usage();
					opensem(&semset_id, key);
					locksem(semset_id, atoi(argv[2]));
				}
				break;
		case 'u': 
				{
					if(argc != 3)
						usage();
					opensem(&semset_id, key);
					unlocksem(semset_id, atoi(argv[2]));
				}
				break;
		case 'd':
				{
					opensem(&semset_id, key);
					removesem(semset_id);
				}
				break;
		case 'm':
				{
					opensem(&semset_id, key);
					changemode(semset_id, argv[2]);
				}
				break;
		default: usage();
				 break;
	}
	return 0;	
}
