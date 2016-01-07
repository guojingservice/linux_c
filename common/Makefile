
objects = 	main.o \
			dlist.o \
			kfifo.o

comtest : CFLAGS = -g

comtest : $(objects)
	cc ${CFLAGS} -o comtest $(objects) -lpthread

main.o : comtest.h

dlist.o : dlist.h
kfifo.o : kfifo.h util.h
.PHONY: clean

clean :
	-rm comtest $(objects)


