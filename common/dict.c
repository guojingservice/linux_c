#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <sys/time.h>
#include <ctype.h>
#include <limits.h>
#include "dict.h"

static int dict_can_resize = 1;
static unsigned int dict_force_resize_ratio = 5;


static int _dictExpandIfNeeded(dict *ht);
static unsigned long _dictNextPower(unsigned long size);
static int _dictKeyIndex(dict *ht, const void *key);
static int _dictInit(dict *ht, dictType *type, void *privDataPtr);

static int _dictExpandIfNeeded(dict *d){
    // incremental rehashing already in process . return
    if(dictIsRehashing(d)) return DICT_OK;
    // if the hash table is empty expand it to the initial size
    if(d->ht[0].size == 0) return dictExpand(d, DICT_HT_INITIAL_SIZE);
    
    if(d->ht[0].used >= d->ht[0].size &&
            (dict_can_resize ||
             d->ht[0].used/d->ht[0].size > dict_force_resize_ratio)){
        return dictExpand(d, d->ht[0].used*2);
    }
    return DICT_OK;
}


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

static int _dictKeyIndex(dict *d, const void *key){
    unsigned int h, idx, table;
    dictEntry *he;

    // expand the hash table if needed
    if(_dictExpandIfNeeded(d) == DICT_ERR){
        return -1;
    }

    // compute the key hash value
    h = dictHashKey(d, key);
    
    for(table = 0; table <= 1; table++){
        idx = h & d->ht[table].sizemask;
        he = d->ht[table].table[idx];
        while(he){
            if(dictCompareKeys(d, key, he->key))
                return -1;
            he = he->next;
        }
        if(!dictIsRehashing(d)) break;
    }
    return idx;
}   


static unsigned long _dictNextPower(unsigned long size){
    unsigned long i = DICT_HT_INITIAL_SIZE;

    if(size >= LONG_MAX) return LONG_MAX;
    while(1){
        if( i >= size) return i;
        i *=2;
    }
}

static void _dictRehashStep(dict *d){
    if(d->iterators == 0) dictRehash(d, 1);
}
/*
 * perform n steps of incremental rehashing. return 1 if there are still
 * keys to move from the old to the new hash table,otherwise 0 is returned
 *
 *
 *
 */
int dictRehash(dict *d, int n){
    int empty_visits = n*10; //max number of empty buckets to visit
    if(!dictIsRehashing(d)) return 0;
    
    while(n-- && d->ht[0].used != 0){
        dictEntry *de, *nextde;
        assert(d->ht[0].size > (unsigned long)d->rehashidx);

        while(d->ht[0].table[d->rehashidx] == NULL){
            d->rehashidx++;
            if(--empty_visits == 0) return 1;
        }
        de = d->ht[0].table[d->rehashidx];
        // move all keys in this bucket from old to the new
        while(de){
            unsigned int h;

            nextde = de->next;

            // fetch the index in the new hash table
            h = dictHashKey(d, de->key) & d->ht[1].sizemask;
            de->next = d->ht[1].table[h];
            d->ht[1].table[h] = de;
            d->ht[0].used--;
            d->ht[1].used++;
            de = nextde;
        }
        d->ht[0].table[d->rehashidx] = NULL;
        d->rehashidx++;

    }
    //check if we already rehash the whole table
    if(d->ht[0].used == 0){
        free(d->ht[0].table);
        d->ht[0] = d->ht[1];
        _dictReset(&d->ht[1]);
        d->rehashidx = -1;
        return 0;
    }

    // need more
    return 1;
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

// add an element to the targe hash table
int dictAdd(dict *d, void *key, void *val){
    dictEntry *entry = dictAddRaw(d, key);

    if(!entry) return DICT_ERR;
    dictSetVal(d, entry, val);
    return DICT_OK;
}

dictEntry *dictAddRaw(dict *d, void *key){
    int index;
    dictEntry *entry;
    dictht *ht;
    if(dictIsRehashing(d)) _dictRehashStep(d);

    if((index = _dictKeyIndex(d, key)) == -1)
        return NULL;

    // allocate the memory and store the new entry
    ht = dictIsRehashing(d) ? &d->ht[1] : &d->ht[0];
    entry = (dictEntry *)malloc(sizeof(*entry));
    entry->next = ht->table[index];
    ht->table[index] = entry;
    ht->used++;

    // set the hash entry fields
    dictSetKey(d,entry, key);
    return entry;
}
// add an element,discard the old if existed
// return 1 if the key was added from scratch,0
// if there was already an element with such key
int dictReplace(dict *d, void *key, void *val){
    dictEntry *entry, auxentry;

    // try to add the element. If the key does not
    // exists dictAdd will succed.
    if(dictAdd(d, key, val) == DICT_OK)
        return 1;

    entry = dictFind(d, key);
    //set the new value and free the old one
    auxentry = *entry;
    dictSetVal(d, entry, val);
    dictFreeVal(d, &auxentry);
}


dictEntry *dictReplaceRaw(dict *d, void *key){
    dictEntry *entry = dictFind(d, key);
    return entry ? entry : dictAddRaw(d, key);
}

// search and remove an element
static int dictGenericDelete(dict *d, const void *key,
        int nofree){
    unsigned int h, idx;
    dictEntry *he, *prevHe;
    int table;
    if(d->ht[0].size == 0) return DICT_ERR;
    if(dictIsRehashing(d)) _dictRehashStep(d);

    h = dictHashKey(d, key);
    for(table=0; table <=1; table++){
        idx = h & d->ht[table].sizemask;
        he = d->ht[table].table[idx];
        prevHe = NULL;

        while(he){
            if(dictCompareKeys(d, key, he->key)){
                if(prevHe)
                    prevHe->next = he->next;
                else
                    d->ht[table].table[idx] = he->next;
                if(!nofree){
                    dictFreeKey(d, he);
                    dictFreeVal(d, he);
                }
                free(he);
                d->ht[table].used--;
                return DICT_OK;
            }
            prevHe = he;
            he = he->next;
        }
        if(!dictIsRehashing(d)) break;
    }
    return DICT_ERR;
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


