/*
*  Author : Guojing
*  Time	  : 2015/6/18
*/


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

#define MAX_EVENT_COUNT 64

static void set_address( char *hname, char *sname, struct sockaddr_in *sap, char *protocol )
{
	struct servent *sp;
	struct hostent *hp;
	char *endptr;
	short port;
	bzero( sap, sizeof(*sap));
	if( hname != NULL )
	{
		if( !inet_aton( hname, &sap->sin_addr ))
		{
			hp = gethostbyname( hname );
			if( NULL == hp )
			{
				perror("unknown host ");
				exit(1);
			}
			sap->sin_addr = *(struct in_addr *)hp->h_addr;
		}
	}
	else
		sap->sin_addr.s_addr = htonl( INADDR_ANY );
	port = strtol( sname, &endptr, 0 );
	if( *endptr == '\0' )
	{
			sap->sin_port = htons(port);
	}
	else
	{
		sp = getservbyname( sname, protocol );
		if( NULL == sp )
		{
			perror("unknown service");
			exit(1);	
		}
		sap->sin_port = sp->s_port;
	}
}

static int make_socket_non_blocking( int sfd )
{
	int flags, s;
	flags = fcntl(sfd, F_GETFL, 0);
	if( -1 == flags )
	{
		perror("fcntl failed!"), exit(1);
	}
	flags |= O_NONBLOCK;
	s = fcntl(sfd, F_SETFL, flags);
	if( -1 == s)
	{
		perror("fctnl set failed!"), exit(1);
	}
	return 0;
}

static int create_and_bind(char *host, char *port)
{
	struct sockaddr_in local;
	int sd = 0;
	const int on = 1;
	set_address(host, port, &local, "tcp");
	sd = socket( AF_INET, SOCK_STREAM, 0 );
	if( sd < 0 )
		perror("create socket failed!"), exit(1);

	if( setsockopt( sd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on)))
	{
		perror("setsockopt failed!"), exit(1);
	}

	make_socket_non_blocking(sd);
	
	if( bind( sd, (struct sockaddr *) &local, sizeof(local)))
		perror("bind failed!"), exit(1);	

	if(listen(sd, 5))
		perror("listen failed!"), exit(1);
	return sd;
}


int main(int argc, char **argv)
{
	int efd;
	int sfd, s;
	struct epoll_event event;
	struct epoll_event* events;

	sfd = create_and_bind("0.0.0.0", "6223");

	efd = epoll_create1(0);
	if(-1 == efd)
		perror("epoll_create failed!"), exit(1);

	event.data.fd = sfd;
	event.events = EPOLLIN | EPOLLET;
	int iRet = epoll_ctl(efd, EPOLL_CTL_ADD, sfd, &event);
	if( -1 == iRet )
		perror("epoll_ctl failed!"), exit(1);

	// buffer where events are returned
	events = calloc(MAX_EVENT_COUNT, sizeof(event));

	// the event loop
	while(1)
	{
		int n, i;
		n = epoll_wait(efd, events, MAX_EVENT_COUNT, -1);
		for( i=0; i < n; ++i )
		{
			if((events[i].events & EPOLLERR) ||
				(events[i].events & EPOLLHUP) ||
				(!events[i].events & EPOLLIN)
			)
			{
				fprintf(stderr, "epoll error\n");
				close(events[i].data.fd);
				continue;
			}
			else if( sfd == events[i].data.fd )
			{
				// this means one more connections come to our listen socket
				while(1)
				{
					struct sockaddr in_addr;
					char hbuf[32];
					char sbuf[32];
					int infd;
					int in_len = sizeof(in_addr);
					infd = accept(sfd, &in_addr, &in_len);
					if( -1 == infd )
					{
						if(( errno == EAGAIN)
							|| (errno == EWOULDBLOCK))
						{
							// we have processed all incoming connections
							break;
						}
						else
						{
							perror("accept");
							break;
						}
					}

					s = getnameinfo(&in_addr, in_len, 
							hbuf, sizeof(hbuf),
							sbuf, sizeof(sbuf),
							NI_NUMERICHOST | NI_NUMERICSERV
						);
					if( 0 == s )
					{
						printf("Accepted connection on descriptor %d, host:%s, port %s\n", 
								infd,
								hbuf,
								sbuf
							);
					}
					// Make incoming socket non-blocking 
					s = make_socket_non_blocking(infd);
					if(s == -1)
						perror("set nonblocking failed!"), exit(1);

					event.data.fd = infd;
					event.events = EPOLLIN | EPOLLET;
					s = epoll_ctl(efd, EPOLL_CTL_ADD, infd, &event);
					if( -1 == s )
					{
						perror("epoll_ctl failed!"), exit(1);
					}

				}
				continue;
			}
			else
			{
					// have data on the fd waiting to be read

				int done = 0;
				char tempBuf[128] = {0};
				while(1)
				{
					char buf[512];
					int count = read(events[i].data.fd, buf, sizeof(buf));
					if( -1 == count )
					{
						// if errno == EAGAIN, then means we have read all data
						if( errno != EAGAIN )
						{
							perror("read failed!"), exit(1);
						}
						break;

					}
					else if( 0 == count)
					{
						// end of file. The remote has closed the connection 
						done =1;
						break;
					}
					//int getpeername(int sockfd, struct sockaddr *addr, socklen_t *addrlen);
					// fetch peer ip
					struct sockaddr_in incom_addr;
					int sockLen = sizeof(incom_addr);
					iRet = getpeername(events[i].data.fd, (struct sockaddr *)&incom_addr, &sockLen);
					if( 0 == iRet )
					{
						char *pId = (char *)inet_ntoa((incom_addr.sin_addr));
						//strcpy(tempBuf, inet_ntoa(addr.sin_addr));
						//char *pPeerIp = inet_ntoa(addr.sin_addr);
						//sprintf(temp, "%s\n", pPeerIp);
						//write(1, temp, strlen(temp));
						printf("Incoming request , source Ip : %s\n\n", pId);
					}
					s = write(1, buf, count);
					if( -1 == s)
					{
						perror("write failed!"), exit(1);
					}
				}
				if(done)
				{
					printf("Closed connection on descriptor :%d\n", events[i].data.fd);
					// closing the descriptor will make epoll remove it from the set of descriptor which are monitored.
					close(events[i].data.fd);
				}

			}
			
			
		}



	}
	free(events);
	close(sfd);
	return 0;
}
