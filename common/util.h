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


#endif
