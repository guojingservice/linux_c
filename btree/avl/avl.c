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

#define UNB_LL  0 // unbalance type of left left, 00
#define UNB_LR  2 // unbalance type of left right, 10
#define UNB_RR  3 // unbalance type of right right, 11
#define UNB_RL  1 // unbalance type of right left , 01

const int LAST_TWO_BIT = 3; // low two bit is 1

int NEED_CH_BR = 0;  
// whether need to change current node's br, used when recursive recall,(递归回溯的时候) 
int ERR_FLAG = 0;	
// whether exist duplicate data, insert failed!



#define ROUTINE_RECORD( bit_record, direction )\
 do\
 {\
 	bit_record = bit_record << 1;\
 	bit_record = bit_record | direction;\
 	bit_record = bit_record & BIT_LOW_FOUR_MASK;\
 }while(0)

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
void ll_rotate( T_NODE **pRoot )
{
	T_NODE *pTempLeft = (*pRoot)->pLeft;
	T_NODE *pTempRoot = *pRoot;

	*pRoot = (*pRoot)->pLeft;
	pTempRoot->pLeft = pTempLeft->pRight;
	pTempLeft->pRight = pTempRoot;

	// refactor bf
	pTempRoot->bf = 0;
	pTempLeft->bf = 0;
}

// 右右
void rr_rotate( T_NODE **pRoot )
{
	T_NODE *pTempRight = (*pRoot)->pRight;
	T_NODE *pTempRoot = *pRoot;

	*pRoot = (*pRoot)->pRight;
	pTempRoot->pRight = pTempRight->pLeft;
	pTempRight->pLeft = pTempRoot;

	// refactor bf
	pTempRoot->bf = 0;
	pTempRight->bf = 0;
}
// 左右
void lr_rotate( T_NODE **pRoot )
{
	T_NODE *pOri = *pRoot; 
	T_NODE *pL1 = (*pRoot)->pLeft;
	T_NODE *pL2 = (*pRoot)->pLeft->pRight;

	(*pRoot)->pLeft = pL2;
	pL1->pRight = pL2->pLeft;
	pL2->pLeft = pL1;

	*pRoot = pL2;
	pOri->pLeft = pL2->pRight;
	pL2->pRight = pOri;

	// refactor bf TODO
	int iBf = pL2->bf;
	if( 0 == iBf )
	{
		pOri->bf = 0;
		pL1->bf = 0;
		pL2->bf = 0;
	}
	else if( 1 == iBf )
	{
		pOri->bf = -1;
		pL1->bf = 0;
		pL2->bf = 0;
	}
	else if( -1 == iBf )
	{
		pOri->bf = 0;
		pL1->bf = 1;
		pL2->bf = 0;
	}
	// error occured!
	else
	{
		perror("avl tree is not correct!");
		exit(1);
	}

}
// 右左
void rl_rote( T_NODE **pRoot )
{

	T_NODE *pOri = *pRoot; 
	T_NODE *pL1 = (*pRoot)->pRight;
	T_NODE *pL2 = (*pRoot)->pRight->pLeft;
	
	pOri->pRight = pL2;
	pL1->pLeft = pL2->pRight;
	pL2->pRight = pL1;

	*pRoot = pL2;
	pOri->pRight = pL2->pLeft;
	pL2->pLeft = pOri;
	// refactor bf TODO

	int iBf = pL2->bf;
	if( 0 == iBf )
	{
		pOri->bf = 0;
		pL1->bf = 0;
		pL2->bf = 0;
	}
	else if( 1 == iBf )
	{
		pOri->bf = 0;
		pL1->bf = -1;
		pL2->bf = 0;
	}
	else if( -1 == iBf )
	{
		pOri->bf = 1;
		pL1->bf = 0;
		pL2->bf = 0;
	}
	else
	{
		perror("avl tree is not correct!");
		exit(1);
	}

}


// adapt to balance
void adaptToBalance( T_NODE **pRoot, int iRecord )
{
	switch( (iRecord & LAST_TWO_BIT) )
	{
		case UNB_LL:{

					}
					break;
		case UNB_LR:{

					}
					break;
		case UNB_RR:{

					}
					break;
		case UNB_RL:{

					}
					break;
		default:
				{
					// unexpected error occured!
					ERR_FLAG = 2;
					exit(1);
				}
				break;
	}
}

// select case, and insert !
void selectInsert( T_NODE **pRoot, int iRecord)
{
	int iLastDirection = iRecord & 1;
	T_NODE *pCur = *pRoot;
	// from left child trees
	if( 0 == iLastDirection )
	{
		(pCur->bf)++;
	}
	// from right child trees
	else if( 1== iLastDirection )
	{
		(pCur->bf)--;
	}

	// if bf did not change
	if(pCur->bf == 0) NEED_CH_BR = 0;
	else if(pCur->bf == -1 || pCur->bf == 1) NEED_CH_BR = 1;
	// need balance
	else
	{
		// adapt and change to balance
		adaptToBalance( pRoot, iRecord );
		NEED_CH_BR = 0;
	}

}

// case： 左左 右右 左右 右左
int insert_node( T_NODE **pRoot,  DATA_TYPE data)
{
	int iResult;
	if( NULL == *pRoot )
	{
		*pRoot = node_create(data);
		NEED_CH_BR = 1;
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
		// record recall back path and only save four last steps, 0 present left, 1 present right
		ROUTINE_RECORD( iResult, 0);
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
		// record recall back path and only save four last steps
		ROUTINE_RECORD( iResult, 1 );
	}
	return iResult;
}


int main(int argc, char **argv)
{
	
	return 0;
}
