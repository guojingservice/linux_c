/*
    implementation of dict
    hash table
*/

#ifndef __DICT
#define __DICT

#include <stdint.h>

#define DICT_OK 0
#define DICT_ERR 1

typedef struct dictEntry{
    void *key;
    union{
        void *val;
        uint64_t u64;
        int64_t s64;
        double d;
    } v;
} dictEntry;

typedef struct dictType{
    unsigned int (*hashFunction)(const void *key);
    void *(*keyDup)(void *privdata, const void *key);
    void *(*valDup)(void *privdata, const void *obj);
    int (*keyCompare)(void *privdata, const void *key1, const void *key2);
    void (*keyDestructor)(void *privdata, void *key);
    void (*valDestructor)(void *privdata, void *obj);

} dictType;

// hash table structure. Every dict has two of this for incremental rehash
typedef struct dictht{
    dictEntry **table;
    unsigned long size;
    unsigned long sizemask;
    unsigned long used;
}dictht;

typedef struct dict{
    dictType *type;
    void *privdata;
    dictht ht[2];
    long rehashidx; // rehashing not in progress if this equals -1
    int iterators; // number of iterators currently running

};




/* safe seted to 1 mean dictAdd, dictFind.. could be called while iterating
    otherwize only dictNext() could be called
*/
typedef struct dictIterator{
    dict *d;
    long index;
    int table, safe;
    dictEntry *entry, *nextEntry;
    // unsafe iterator fingerprint for misuse detection
    long long fingerprint;
}dictIterator;

typedef void (dictScanFunction)(void *privdata, const dictEntry *de);

// initial size of every hash table
#define DICT_HT_INITIAL_SIZE 4

#define dictFreeVal(d, entry) \
    if((d)->type->valDestructor) \
        (d)->type->valDestructor((d)->privdata, (entry)->v.val); 

#define dictSetVal(d, entry, _val__ do { \
    if((d)->type->valDup) \
        entry->v.val = (d)->type->valDup((d)->privdata, _val_); \
    else \
        entry->v.val = (_val_); \
    } while(0)

#define dictSetSignedIntegerVal(entry, _val_) \
    do { entry->v.s64 = _val_; } while(0)

#define dictSetUnsignedIntegerVal(entry, _val_) \
    do { entry->v.us64 = _val_; } while(0)

#define dictSetDoubleVal(entry, _val_) \
    do { entry->v.d = _val_;} while(0)


#define dictFreeKey(d, entry) \
    if((d)->type->keyDestructor) \
        (d)->type->keyDestructor((d)->privdata, (entry)->key)

#define dictSetKey(d, entry, _key_) do { \
    if((d)->type->keyDup) \
        entry->key = (d)->type->keyDup((d)->privdata, _key_); \
    else \
        entry->key = (_key_); \ 
    }while(0)


#define dictCompareKeys(d, key1, key2) \
    (((d)->type->keyCompare) ? \
        (d)->type->keyCompare((d)->privdata, key1, key2) : \
        (key1) == (key2))

#define dictHashKey(d, key) (d)->type->hashFunction(key)

#define dictGetKey(he) ((he)->key)

#define dictGetVal(he) ((he)->v.val)

#define dictGetSignedIntegerVal(he) ((he)->v.s64)

#define dictGetUnsignedIntegerVal(he) ((he)->v.u64)

#define dictGetDoubleVal(he) ((he)->v.d)

#define dictSlots(d) ((d)->ht[0].size + (d)->ht[1].size)

#define dictSize(d) ((d)->ht[0].used + (d)->ht[1].used)

#define dictIsRehashing(d) ((d)->rehashidx != -1)

/*
API
*/

dict *dictCreate(dictType *type, void *privDataPtr);



#endif

