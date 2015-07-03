#include "strmap.h"

typedef struct Pair Pair;
typedef struct Bucket Bucket;

struct Pair{
	char *key;
	char *value;
};

struct Bucket{
	unsigned int count;
	Pair *pairs;
};

struct StrMap{
	unsigned int count;
	Bucket *buckets;
};

static Pair *get_pair(Bucket *bucket, const char *key);
static unsigned long hash(const char *str);


// create a string map
StrMap * sm_new(unsigned int capacity)
{
	StrMap *map;
	map = malloc(sizeof(StrMap));
	if( NULL == map )
	{
		perror("malloc StrMap failed!");
		return NULL;
	}
	map->count = capacity;
	map->buckets = malloc(map->count * sizeof(Bucket));
	if( map->buckets == NULL )
	{
		free(map);
		perror("malloc StrMap->buckets failed!");
		return NULL;
	}
	memset(map->buckets, 0, map->count * sizeof(Bucket));
	return map;
}


// release all memory held by a string map object
void sm_delete(StrMap *map)
{
	unsigned int i, j, n,m;
	Bucket *bucket;
	Pair *pair;
	if( NULL == map )
	{
		return;
	}
	n = map->count;
	bucket = map->buckets;
	i  = 0;
	while( i < n )
	{
		m = bucket->count;
		pair = bucket->pairs;
		j = 0;
		while( j < m )
		{
			free(pair->key);
			free(pair->value);
			pair++;
			j++;
		}
		free(bucket->pairs);
		bucket++;
		i++;
	}
	free(map->buckets);
	free(map);
	return;
}

// return the value associated with the supplied key
int sm_get(const StrMap *map, const char *key, char *out_buf, unsigned int n_out_buf)
{
	unsigned int index;
	Bucket *bucket;
	Pair *pair;

	if( map == NULL )
	{
		return 0;
	}
	if( key == NULL )
	{
		return 0;
	}
	index = hash(key) % map->count;
	bucket = &(map->buckets[index]);
	pair = get_pair(bucket, key);
	if( NULL == pair )
	{
		return 0;
	}
	if( out_buf == NULL && n_out_buf == 0 )
	{
		return strlen(pair->value) +1;
	}
	if( NULL == out_buf )
	{
		return 0;
	}
	if( strlen(pair->value) >= n_out_buf )
	{
		return 0;
	}
	strcpy(out_buf, pair->value);
	return 1;
}

// query the existence of a key
int sm_exists(const StrMap *map, const char *key)
{
	unsigned int index;
	Bucket *bucket;
	Pair *pair;

	if( map == NULL )
	{
		return 0;
	}
	if( key == NULL )
	{
		return 0;
	}
	index = hash(key) % map->count;
	bucket = &(map->buckets[index]);
	pair = get_pair(bucket, key);
	if( NULL == pair )
	{
		return 0;
	}
	return 1;
}

// associate a value with a supplied key
int sm_put(StrMap *map, const char *key, const char *value)
{
	unsigned int key_len, value_len, index;
	Bucket *bucket;
	Pair *tmp_pairs, *pair;
	char *tmp_value;
	char *new_key, *new_value;

	if( map == NULL )
	{
		return 0;
	}
	if( NULL == key || NULL == value )
	{
		return 0;
	}
	key_len = strlen(key);
	value_len = strlen(value);
	index = hash(key) % map->count;
	bucket = &(map->buckets[index]);
	// check if could just replacing an existing value in a key_value pair
	if( NULL != (pair = get_pair(bucket, key)))
	{
		if(strlen(pair->value) < value_len)
		{
			tmp_value = realloc(pair->value, (value_len +1) * sizeof(char));
			if( NULL == tmp_value )
			{
				return 0;
			}
			pair->value = tmp_value;
		}
		strcpy(pair->value, value);
		return 1;
	}
	// allocate space for a new key and value
	new_key = malloc((key_len + 1) * sizeof(char));
	if( NULL == new_key )
	{
		return 0;
	}
	new_value = malloc((value_len +1) * sizeof(char));
	if(new_value == NULL )
	{
		free(new_key);
		return 0;
	}
	// create a key-value pair
	if( bucket->count == 0 )
	{
		// the bucket is empty
		bucket->pairs = malloc(sizeof(Pair));
		if( NULL == bucket->pairs )
		{
			free(new_key);
			free(new_value);
			return 0;
		}
		bucket->count = 1;
	}
	else
	{
		// the bucket is not empty
		tmp_pairs = realloc(bucket->pairs, (bucket->count +1) * sizeof(Pair));
		if( NULL == tmp_pairs )
		{
			free(new_key);
			free(new_value);
			return 0;
		}
		bucket->pairs = tmp_pairs;
		bucket->count++;
	}
	// get the last pair in the chain for the bucket
	pair = &(bucket->pairs[bucket->count - 1]);
	pair->key = new_key;
	pair->value = new_value;
	// copy the key and value into the newly allocated memory
	strcpy(pair->key, key);
	strcpy(pair->value, value);
	return 1;
}

// returns the number of associations between keys and values
int sm_get_count(const StrMap *map)
{
	unsigned int i, j, n, m;
	unsigned int count;
	Bucket *bucket;
	Pair *pair;

	if( NULL == map )
	{
		return 0;
	}
	bucket = map->buckets;
	n = map->count;
	i = 0;
	count = 0;
	while( i < n )
	{
		pair = bucket->pairs;
		m = bucket->count;
		j = 0;
		while( j < m )
		{
			count++;
			pair++;
			j++;
		}
		bucket++;
		i++;
	}
	return count;
}

// an enumerator over all associations between keys and values
// return 1 if enumeration completed, 0 failed!
int sm_enum(const StrMap *map, sm_enum_func enum_func, const void *obj)
{
	unsigned int i, j, n, m;
	Bucket *bucket;
	Pair *pair;
	if( NULL == map )
	{
		return 0;
	}
	if( NULL == enum_func )
	{
		return 0;
	}
	bucket = map->buckets;
	n = map->count;
	i = 0;
	while( i < n )
	{
		pair = bucket->pairs;
		m = bucket->count;
		j = 0;
		while( j < m )
		{
			enum_func(pair->key, pair->value, obj);
			pair++;
			j++;
		}
		bucket++;
		i++;
	}
	return 1;
}

static Pair *get_pair(Bucket *bucket, const char *key)
{
	unsigned int i, n;
	Pair *pair;
	n = bucket->count;
	if( 0 == n )
	{
		return NULL;
	}
	pair = bucket->pairs;
	i = 0;
	while( i < n )
	{
		if(pair->key != NULL && pair->value != NULL )
		{
			if(strncmp(pair->key, key, strlen(pair->key)) == 0 )
			{
				return pair;
			}
		}
		i++;
		pair++;
	}
	return NULL;
}

static unsigned long hash(const char *str )
{
	unsigned long hash = 5381;
	int c;
	while( c = *str++ )
	{
		hash = ((hash << 5) + hash ) + c;
	}
	return hash;
}

