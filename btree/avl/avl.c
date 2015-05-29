/*
*	avl tree
*	base functions
*	
*/

#include <stdio.h>
#include <stdlib.h>


typedef int DATA_TYPE;

typedef struct t_node{
	DATA_TYPE 				data;		// data
	int 					bf;			// average element
	struct t_node			*pLeft;		// left child
	struct t_node			*pRight;	// right child
}T_NODE, *P_NODE, *AVL_TREE;

const int BIT_LOW_FOUR_MASK = 0x0f;

int NEED_CH_BR = 0;  
// whether need to change current node's br, used when recursive recall,(递归回溯的时候) 
int ERR_FLAG = 0;	
// whether exist duplicate data, insert failed!

T_NODE* node_create(DATA_TYPE data)
{
	T_NODE *pNewNode = malloc(sizeof(T_NODE));
	pNewNode->data = data;
	pNewNode->bf = 0;
	pNewNode->pLeft = NULL;
	pNewNode->pRight = NULL;
	return pNewNode;
}

void node_free( T_NODE **pNode )
{
	if( NULL != pNode && *pNode != NULL )
	{
		free(*pNode);
		*pNode = NULL;
	}
}

void print_data( DATA_TYPE *pData)
{
	printf("%d ", *pData);
}

void pre_display( T_NODE *pRoot )
{
	if( NULL == pRoot )
	{
		return;
	}
	print_data( &(pRoot->data) );
	pre_display( pRoot->pLeft );
	pre_display( pRoot->pRight );
}

void infi_display( T_NODE *pRoot )
{
	if( NULL == pRoot )
	{
		return;
	}
	infi_display( pRoot->pLeft );
	print_data( &(pRoot->data) );
	infi_display( pRoot->pRight ); 
}

void back_display( T_NODE *pRoot )
{
	if( NULL == pRoot )
	{
		return;
	}
	back_display( pRoot->pLeft );
	back_display( pRoot->pRight );
	print_data( &(pRoot->data));
}

// 左左
void ll_rotate( T_NODE *pRoot )
{

}

// 右右
void rr_rotate( T_NODE *pRoot )
{

}
// 左右
void lr_rotate( T_NODE *pRoot )
{

}
// 右左
void rl_rote( T_NODE *pRoot )
{
	
}
// case： 左左 右右 左右 右左
int insert_node( T_NODE **pRoot,  DATA_TYPE data)
{
	int iResult;
	if( NULL == *pRoot )
	{
		*pRoot = node_create(data);
		return 0;
	}
	if( (*pRoot)->data == data )
	{
		printf("same data exist! insert failed!");
		ERR_FLAG = 1;
		return -1;
	}
	// insert left tree
	if( (*pRoot)->data > data )
	{
		iResult = insert_node( &((*pRoot)->pLeft), data );
		// exist same data, insert failed!
		if( ERR_FLAG )
		{
			return iResult;
		}
	}
	// insert right tree
	else if( (*pRoot)->data < data )
	{
		iResult = insert_node( &((*pRoot)->pRight), data );
		// exist same data, insert failed!
		if( ERR_FLAG )
		{
			return iResult;
		}
	}
}


int main(int argc, char **argv)
{
	
	return 0;
}
