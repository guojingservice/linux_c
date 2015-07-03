#ifndef _STR_MAP_H
#define _STR_MAP_H

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

typedef struct StrMap StrMap;

typedef void(*sm_enum_func)(const char *key, const char *value, const void *obj);


// create a string map
StrMap * sm_new(unsigned int capacity);

// release all memory held by a string map object
void sm_delete(StrMap *map);

// return the value associated with the supplied key
int sm_get(const StrMap *map, const char *key, char *out_buf, unsigned int n_out_buf);

// query the existence of a key
int sm_exists(const StrMap *map, const char *key);

// associate a value with a supplied key
int sm_put(StrMap *map, const char *key, const char *value);

// returns the number of associations between keys and values
int sm_get_count(const StrMap *map);

// an enumerator over all associations between keys and values
// return 1 if enumeration completed, 0 failed!
int sm_enum(const StrMap *map, sm_enum_func enum_func, const void *obj);

#endif






