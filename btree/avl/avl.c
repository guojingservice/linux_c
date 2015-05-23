#include <stdio.h>

typedef int DATA_TYPE;

typedef struct t_node{
	DATA_TYPE 		data;
	struct t_node			*pLeft;
	struct t_node			*pRight;	
}T_NODE, *P_NODE;

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

int main(int argc, char **argv)
{
	
	return 0;
}
