COMM_CFILE = $(wildcard *.c)
COMM_OBJ = $(COMM_CFILE:.c=.o)
COMM_LIB=../lib/libcomm.a
COMM_SO=../lib/libcomm.so
COMM_IMP_LIB = -lpthread
COMM_UNIT_TEST = comtest
.PHONY: all clean

$(COMM_UNIT_TEST): CFLAGS = -g

all: $(COMM_LIB) $(COMM_SO) $(COMM_UNIT_TEST)

-include $(COMM_CFILE:.c=.d)

%.d:%.c
	$(CC) -MM $(CFLAGS) $< -o $@

%.o:%.c %.d
	$(CC) -c $(CFLAGS) $<

$(COMM_LIB): $(COMM_OBJ)
	ar r $(COMM_LIB) $^

$(COMM_SO): $(COMM_OBJ)
	$(CC) -o $(COMM_SO) $(SHARED) $(CFLAGS)  $(COMM_IMP_LIB) $^

$(COMM_UNIT_TEST) : $(COMM_OBJ)
	$(CC) -o $@ $(CFLAGS) $(COMM_IMP_LIB)  $(COMM_OBJ)

clean :
	-rm *.o *.d
	-rm $(COMM_LIB)
	-rm $(COMM_SO)


