#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/msg.h>
#include <string.h>
#include <errno.h>
struct client_info{
	long cmd;
	char text[2048];
};


struct my_msgbuf{
	long mtype;
	long request_id;
	struct client_info info;
};

int open_queue( key_t keyval )
{
	int qid;
	if((qid = msgget( keyval, IPC_CREAT | 0660)) == -1)
	{
		return -1;
	}
	return qid;
}

int send_message( int qid, struct my_msgbuf *qbuf)
{
	int result, length;
	length = sizeof(struct my_msgbuf) - sizeof(long);
	if((result = msgsnd( qid, qbuf, length, 0)) == -1)
	{
		return -1;
	}
	return result;
}

int read_message( int qid, long type, struct my_msgbuf *qbuf )
{
	int result, length;
	// length is essentially the size of the structure minus sizeof(mtype)
	length = sizeof(struct my_msgbuf) - sizeof(long);
	if((result = msgrcv( qid, qbuf, length, type, 0)) == -1)
	{
		return -1;
	}
	return result;
}

int peek_message(int qid, long type)
{
	int result, length;
	
	if((result = msgrcv( qid, NULL, 0, type, IPC_NOWAIT)) == -1)
	{
		if( errno == E2BIG )
			return 0;
	}
	return -1;
}

// IPC_STAT ex
int get_queue_ds( int qid, struct msqid_ds *qbuf)
{	
	if( msgctl( qid, IPC_STAT, qbuf) == -1 )
	{
		return -1;
	}
	return 0;
}

// IPC_SET ex
int change_queue_mode(int qid, char *mode)
{
	struct msqid_ds tmpbuf;
	// retieve a current copy of internal data structure
	int iRet = get_queue_ds( qid, &tmpbuf);
	if(iRet != 0 )
	{
		perror("get_queue_ds");
		exit(1);
	}
	// change permissions using an old trick
	sscanf(mode, "%ho", &tmpbuf.msg_perm.mode);
	// update the internal data structure
	if( msgctl( qid, IPC_SET, &tmpbuf) == -1)
	{
		perror("msgctl");
		return -1;
	}
	return 0;
}
// remove queue
int remove_queue( int qid )
{
	if( msgctl( qid, IPC_RMID, 0) == -1)
	{
		return -1;
	}
	return 0;
}

int main(int argc, char **argv)
{
	int qid;
	key_t msgkey;
	struct my_msgbuf my_msg;
	printf("input qid :\n");
	scanf("%d", &qid);
	int choice;
	printf("input choice: 1 -> read message   2 -> remove message\n");
	scanf("%d", &choice);
	switch(choice)
	{
		case 1:{
				int iRet = read_message(qid, 1, &my_msg);
				if( iRet == -1)
				{
					perror("read_message failed!");
					exit(1);
				}
				printf("mtype : %d\n", my_msg.mtype);
				printf("info:cmd : %d\n", my_msg.info.cmd);
				printf("info:text : %s\n", my_msg.info.text);
		       }
		       break;
		case 2:{
				int iRet = remove_queue(qid );
				if( iRet == -1)
				{
					perror("remove message failed!");
					exit(1);
				}		
				printf("remove queue success!");
		       }
		       break;
		default:
			{
				printf("invalid choice!\n");
				exit(1);
			}
			break;
	}
	

	return 0;
}
