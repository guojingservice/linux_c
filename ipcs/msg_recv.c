#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/msg.h>
#include <string.h>

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
	int qid;
	key_t msgkey;
	struct my_msgbuf my_msg;
	my_msg.mtype = 1;
	my_msg.request_id = 1;
	my_msg.info.cmd = 1;
	strcpy(my_msg.info.text, "hello world!");
	
	// gen msg key
	msgkey = ftok(".", 'm');
	
	if((qid = open_queue(msgkey)) == -1)
	{
		perror("open queue");
		exit(1);
	}
	
	// send msg
	
	if((send_message( qid, &my_msg )) == -1)
	{
		perror("send message!");
		exit(1);
	}
	
	printf("send finished with no error!\n");
	return 0;
}
