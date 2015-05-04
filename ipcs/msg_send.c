#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/msg.h>

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

int main(int argc, char **argv)
{

	return 0;
}
