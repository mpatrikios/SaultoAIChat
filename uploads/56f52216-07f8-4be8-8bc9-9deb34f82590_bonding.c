#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include "dllist.h"
#include "bonding.h"

// bonding.h includes
// - new_mutex = allocates and initializes a pthread_mutex_t
// - new_cond = allocates and initializes a pthread_cond_t

// bonding driver creates a creator thread and joiner thread
// - creator thread creates hydrogen and oxygen threads with pthread_create
// - joiner thread cleans up hydrogen and oxygen threads when they are returned and frees creator thread

// gloabl data struct to hold mutex and two dllists
typedef struct global_struct {
	pthread_mutex_t *mutex;
	Dllist hydrogen_list;
	Dllist oxygen_list;
} GlobalInfo;

// each thread will have its own struct, 
// contains a condition, thread id's, and id's of the 3 threads of the molecule
typedef struct thread_data {
	int id;                 
	pthread_cond_t *cond;   
	int h1;                 
	int h2;                
	int o;                  
} ThreadData;

// allocatre and initialize the data structure
void *initialize_v(char *verbosity)
{
	GlobalInfo *g = (GlobalInfo *) malloc(sizeof(GlobalInfo));
	g->mutex = new_mutex();
	g->hydrogen_list = new_dllist();
	g->oxygen_list = new_dllist();

	return (void *) g;
}

// hydrogren thread
// param: struct bonding arg, contains id for the thread and a void* to store data
// arg->v is a pointer to the global struct
// arg->id is the thread id
void *hydrogen(void *arg){
	struct bonding_arg *a = (struct bonding_arg *) arg;
	GlobalInfo *g = (GlobalInfo *) a->v;
	ThreadData *data, *odata, *hdata;
	char *rv;
	Dllist tmp, oxygen_nodes, onode, hnode;

	// create new thread data struct and lock mutex
	data = (ThreadData *) malloc(sizeof(ThreadData));
	data->id = a->id;
	data->cond = new_cond();
	data->h1 = -1;
	data->h2 = -1;
	data->o = -1;

	pthread_mutex_lock(g->mutex);

	// look at waiting list, need 1 hydrogen and 1 oxygen
	if (!dll_empty(g->oxygen_list) && !dll_empty(g->hydrogen_list)) {
		// get oxygen node
		onode = dll_first(g->oxygen_list);
		odata = (ThreadData *) onode->val.v;

		// get hydrogen node
		hnode = dll_first(g->hydrogen_list);
		hdata = (ThreadData *) hnode->val.v;

		// remove them from the list
		dll_delete_node(onode);
		dll_delete_node(hnode);

		// set 3 thread ids
		data->h1 = hdata->id;
		data->h2 = a->id;
		data->o = odata->id;

		// need to set ids for each molecule
		hdata->h1 = data->h1;
		hdata->h2 = data->h2;
		hdata->o = data->o;

		odata->h1 = data->h1;
		odata->h2 = data->h2;
		odata->o = data->o;

		// call pthread_cond_signal() on the two threads
		pthread_cond_signal(hdata->cond);
		pthread_cond_signal(odata->cond);

		// unlock mutex
		pthread_mutex_unlock(g->mutex);

		// call Bond() on the three ids and store return value
		rv = Bond(data->h1, data->h2, data->o);

		// free memory and destroy condition variable
		pthread_cond_destroy(data->cond);
		free(data);

		// return the value
		return (void *) rv;
	}
	// if it can't, add itself to list and block
	else{
		dll_append(g->hydrogen_list, new_jval_v(data));

		// block until it can create a molecule
		pthread_cond_wait(data->cond, g->mutex);

		// unlock mutex when returned from wait
		pthread_mutex_unlock(g->mutex);

		// call bond() on the three ids and store return value
		rv = Bond(data->h1, data->h2, data->o);

		// free memory
		pthread_cond_destroy(data->cond);
		free(data);

		// return the value
		return (void *) rv;
	}
}

// oxygen thread
// param: struct bonding arg, contains id for the thread and a void* to store data
void *oxygen(void *arg)
{
	struct bonding_arg *a = (struct bonding_arg *) arg;
	GlobalInfo *g = (GlobalInfo *) a->v;
	ThreadData *data, *hdata1, *hdata2;
	char *rv;
	Dllist tmp, oxygen_nodes, h1node, h2node;
	int count = 0;  

	// create new thread data struct
	data = (ThreadData *) malloc(sizeof(ThreadData));
	data->id = a->id;
	data->cond = new_cond();
	data->h1 = -1;
	data->h2 = -1;
	data->o = -1;

	// lock mutex
	pthread_mutex_lock(g->mutex);

	dll_traverse(tmp, g->hydrogen_list) {
		count++;
	}

	// need at least 2 hydrogen atoms
	if (count >= 2) {
		// Get first hydrogen node 
		h1node = dll_first(g->hydrogen_list);
		hdata1 = (ThreadData *) h1node->val.v;

		// remove from the list
		dll_delete_node(h1node);

		// get next hydrogen node 
		h2node = dll_first(g->hydrogen_list);
		hdata2 = (ThreadData *) h2node->val.v;

		// remove from the list
		dll_delete_node(h2node);

		// set 3 thread ids
		data->h1 = hdata1->id;
		data->h2 = hdata2->id;
		data->o = a->id;

		// need to set ids for all molecules
		hdata1->h1 = data->h1;
		hdata1->h2 = data->h2;
		hdata1->o = data->o;

		hdata2->h1 = data->h1;
		hdata2->h2 = data->h2;
		hdata2->o = data->o;

		//call pthread_cond_signal() on the two threads
		pthread_cond_signal(hdata1->cond);
		pthread_cond_signal(hdata2->cond);

		// unlock mutex
		pthread_mutex_unlock(g->mutex);

		// call Bond() on the three ids and store return value
		rv = Bond(data->h1, data->h2, data->o);

		// free memory
		pthread_cond_destroy(data->cond);
		free(data);

		// return the value
		return (void *) rv;
	}
	// if it can't, add itself to list and block
	else{
		dll_append(g->oxygen_list, new_jval_v(data));

		// block until it can create a molecule
		pthread_cond_wait(data->cond, g->mutex);

		// unlock mutex when returned from wait
		pthread_mutex_unlock(g->mutex);

		// call bond() on the three ids and store return value
		rv = Bond(data->h1, data->h2, data->o);

		// free memory
		pthread_cond_destroy(data->cond);
		free(data);

		// return the value
		return (void *) rv;
	}
}
