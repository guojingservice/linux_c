
objects = main.o dlist.o


comtest : $(objects)
	cc -o comtest $(objects)
    
main.o : main.c
	cc -c main.c
dlist.o : dlist.c
	cc -c dlist.c


clean :
	rm comtest $(objects)


