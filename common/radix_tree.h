#ifndef _RADIX_TREE_H
#define _RADIX_TREE_H


/*
 * radix tree implement
 * associate id with ptr
 *
 */

#define RADIX_NODE_NO_VALUE NULL


struct radix_node{
    struct radix_node *left;
    struct radix_node *right;
    struct radix_node *parrent;
    void              *data;
};

struct radix_tree{
    struct radix_node *root;
    struct radix_node *free;
    struct radix_node *

};


#endif
