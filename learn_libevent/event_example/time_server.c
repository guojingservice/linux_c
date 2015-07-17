#include <stdio.h>
#include <stdlib.h>
#include <event.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <time.h>

void connection_time( int fd, short event, struct event *arg )
{
	char buf[32];
	struct tm t;
	time_t now;

	time(&now);
	localtime_r(&now, &t);
	asctime_r(&t, buf);

	write(fd,buf, strlen(buf));
	shutdown(fd, SHUT_RDWR);
	free(arg);
}

void connection_accept(int fd, short event, void *arg)
{
	fprintf(stderr, "%s():fd = %d, event = %d.\n", __func__, fd, event);

	// accept a new connection
	struct sockaddr_in s_in;
	socklen_t len = sizeof(s_in);
	int ns = accept(fd, (struct sockaddr *)&s_in, &len);
	if( ns < 0 )
	{
		perror("accept");
		return;		
	}

	// install time server
	struct event *ev = malloc(sizeof(struct event));
	event_set(ev, ns, EV_WRITE, (void *)connection_time, ev);
	event_add(ev,NULL);
}

int main(int argc, char **argv)
{
	// request socket
	int s = socket(AF_INET, SOCK_STREAM, 0 );
	if( s < 0 )
	{
		perror("socket!");
		exit(1);
	}

	//bind
	struct sockaddr_in s_in;
	bzero(&s_in, sizeof(s_in));

	s_in.sin_family = AF_INET;
	s_in.sin_port	= htons(8700);
	s_in.sin_addr.s_addr = INADDR_ANY;

	if( bind(s, (struct sockaddr *) &s_in, sizeof(s_in)) < 0 )
	{
		perror("bind error!");
		exit(1);
	}

	// listen()
	if( listen(s, 5) < 0 )
	{
		perror("listen error!");
		exit(1);
	}

	// initial libevent
	event_init();

	// create event
	struct event ev;
	event_set(&ev, s, EV_READ | EV_PERSIST, connection_accept, &ev);

	// add event
	event_add(&ev, NULL);
	event_dispatch();
	return 0;
}
