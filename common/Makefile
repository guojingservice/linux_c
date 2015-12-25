
objects = main.o dlist.o
hobjects = dlist.h klist.h util.h

comtest : $(objects) $(hobjects)
	cc -o comtest $(objects)
    
main.o : main.c klist.h
	cc -c main.c
#dlist.o : dlist.c
#	cc -c dlist.c


clean :
	rm comtest $(objects)


