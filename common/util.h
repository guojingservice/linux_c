#ifndef _UTIL_H
#define _UTIL_H


/*
 * return the offset of a structure's member 
 *
 * @type: type of the structure
 * @member: member of the structure
 *
 */
#define offsetof(type, member) ((size_t) &((type *)0)->member)



/*
 * cast a member of a structure out to the containing structure
 *
 * @ptr: the pointer to the member.
 * @type: the type of the container struct this is embedded in.
 * @member: the name of the member within the struct.
 *
 */
#define container_of(ptr, type, member) ({  \
    const typeof( ((type *)0)->member ) *__mptr = (ptr);    \
    (type *)( (char *)__mptr - offsetof(type, member));})

static inline int is_power_of_2(unsigned int n)
{
    return ( n != 0 && ( (n & (n - 1)) == 0 ));
}

/*
 * find the left most bit
 * @fig: the figure to find
 */
static inline unsigned int left_most_bit(unsigned int fig){
    int ret = 0;
    while( fig > 0){
        fig = fig >> 1;
        ++ret;
    }
    return ret;
}

/*
 * find the right most bit
 */
static inline unsigned int right_most_bit(unsigned int fig){
    int ret = 0;
    while( (fig & 0x1) > 0){
        ++ret;
        fig = fig >> 1;
    }
}

/*
 * round up to power of 2
 *
 */
static inline unsigned int roundup_power_of_2(unsigned int fig){
    return fig == 0 ? 2 : 1 << (left_most_bit(fig) + 1);
}

// (void) (&__min1 == &__min2)  is preventing the comparison of different types
#define min(x, y) ({    \
    typeof(x) __min1 = (x); \
    typeof(y) __min2 = (y); \
    (void) (&__min1 == &__min2);    \
    __min1 < __min2 ? __min1 : __min2;  \
})

#define max(x,y) ({ \
    typeof(x) __max1 = (x); \
    typeof(y) __max2 = (y); \
    (void) (&__max1 == &__max2);    \
    __max1 > __max2 ? __max1 : __max2;  \
})

#define swap(a,b) \
    do { typeof(a) __tmp = (a); (a) = (b); (b) = __tmp;} while(0)


#endif
