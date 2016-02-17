#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <sys/time.h>
#include <ctype.h>
#include "dict.h"

static int dict_can_resize = 1;
static unsigned int dict_force_resize_ratio = 5;

static void _dictReset(dictht *ht){
    ht->table = NULL;
    ht->size = 0;
    ht->sizemask = 0;
    ht->used = 0;
}

int _dictInit(dict *d, dictType *type, void *privDataPtr){
    _dictReset(&d->ht[0]);
    _dictReset(&d->ht[1]);
    d->type = type;
    d->privdata = privDataPtr;
    d->rehashidx = -1;
    d->iterators = 0;
    return DICT_OK;
}

// create the new hash table
dict *dictCreate(dictType *type, void *privDataPtr){
    dict *d = (dict *)malloc(sizeof(*d));
    
    _dictInit(d, type, privDataPtr);
    return d;
}

// expand or create the table
int dictExpand(dict *d, unsigned long size){
    dictht n; // the new hash table
    unsigned long realsize = _dictNextPower(size);

    // the size is invalid if it is smaller than 
    // the number of elements already inside the hash table
    if(dictIsRehashing(d) || d->ht[0].used > size)
        return DICT_ERR;
    // resize to the same table size is not useful
    if(realsize == d->ht[0].size) return DICT_ERR;
    
    // allocate the new hash and initialize all pointers to NULL
    n.size = realsize;
    n.sizemask = realsize-1;
    n.table = (dictEntry **)calloc(realsize, sizeof(dictEntry*));
    n.used = 0;
    
    // if this is the first initialization, then just set the first table
    if(d->ht[0].table == NULL){
        d->ht[0] = n;
        return DICT_OK;
    }

    // prepare the second hash table for increment
    d->ht[1] = n;
    d->rehashidx = 0;
    return DICT_OK;
    
}









// stringcopy hash table type
static unsigned int _dictStringCopyHTHashFunction(const void *key){
    return dictGenHashFunction(key, strlen(key));
}

static void *_dictStringDup(void *privdata, const void *key){
    int len = strlen(key);
    char *copy = (char *)malloc(len+1);
    DICT_NOTUSED(privdata);

    memcpy(copy, key, len);
    copy[len] = '\0';
    return copy;
}

static int _dictStringCopyHTKeyCompare(void *privdata, const void *key1,
        const void *key2){
    DICT_NOTUSED(privdata);
    return strcmp(key1, key2) == 0;
}

static void _dictStringDestructor(void *privdata, void *key){
    DICT_NOTUSED(privdata);

    free(key);
}

dictType dictTypeHeapStringCopyKey = {
    _dictStringCopyHTHashFunction, // hash fucntion
    _dictStringDup,                // key dup
    NULL,                          // value dup
    _dictStringCopyHTKeyCompare,   // key compare
    _dictStringDestructor,         // key destrutor
    NULL                           // val destructor
};

dictType dictTypeHeapStrings = {
    _dictStringCopyHTHashFunction,
    NULL,
    NULL,
    _dictStringCopyHTKeyCompare,
    _dictStringDestructor,
    NULL
};

dictType dictTypeHeapStringCopyKeyValue= {
    _dictStringCopyHTHashFunction,
    _dictStringDup,
    _dictStringDup,
    _dictStringCopyHTKeyCompare,
    _dictStringDestructor,
    _dictStringDestructor,
};


