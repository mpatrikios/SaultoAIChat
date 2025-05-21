#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include "jrb.h"
#include "dllist.h"
#include "sockettome.h"

// Helper functions for mutex and condition variables
pthread_mutex_t *new_mutex() {
  pthread_mutex_t *l;
  l = (pthread_mutex_t *) malloc(sizeof(pthread_mutex_t));
  if (l == NULL) { perror("malloc pthread_mutex_t"); exit(1); }
  pthread_mutex_init(l, NULL);
  return l;
}

pthread_cond_t *new_cond() {
  pthread_cond_t *c;
  c = (pthread_cond_t *) malloc(sizeof(pthread_cond_t));
  if (c == NULL) { perror("malloc pthread_cond_t"); exit(1); }
  pthread_cond_init(c, NULL);
  return c;
}

// Struct definitions
typedef struct {
    char *name;
    pthread_mutex_t *mutex;
    pthread_cond_t *cond;
    pthread_t thread_id;
    Dllist client_list;
    Dllist message_list;
} Chatroom;

typedef struct {
    char *name;
    Chatroom* room;
    FILE *input;
    FILE *output;
    pthread_t thread_id;
    int active;
} Client;

// Global variables
JRB chat_rooms;
pthread_mutex_t *rooms_mutex;

// Client thread function
void *client_thread(void *new_client) {
    Client *client = (Client *) new_client;
    char buffer[1024];
    char name[256];
    char room_name[256];
    JRB requested_room, room_tmp;
    Dllist client_tmp, tmp_node;
    Chatroom *room;

    // Print initial chat room information
    fputs("Chat Rooms:\n\n", client->output);
    pthread_mutex_lock(rooms_mutex);
    
    // Print chat rooms and their clients
    jrb_traverse(room_tmp, chat_rooms) {
        room = (Chatroom *) room_tmp->val.v;
        fprintf(client->output, "%s:", room->name); 
        
        pthread_mutex_lock(room->mutex);
        dll_traverse(client_tmp, room->client_list) {
            Client *room_client = (Client *) client_tmp->val.v;
            fprintf(client->output, " %s", room_client->name);   
        }
        pthread_mutex_unlock(room->mutex);
        
        fprintf(client->output, "\n");  
    }

    fprintf(client->output, "\n");
    
    pthread_mutex_unlock(rooms_mutex);
    
    // Get client name
    fputs("Enter your chat name (no spaces):\n", client->output);
    fflush(client->output);
    
    // if read EOF while reading client info, close buffers and kill thread
    if (fgets(buffer, sizeof(buffer), client->input) == NULL) {
        fclose(client->input);
        fclose(client->output);
        free(client);
        return NULL;
    }

    // remove newline char
    size_t len = strlen(buffer);
    if (len > 0 && buffer[len-1] == '\n') {
        buffer[len-1] = '\0';
    }
    client->name = strdup(buffer);
    
    // Get chat room choice
    fputs("Enter chat room:\n", client->output);
    fflush(client->output);
    
    if (fgets(buffer, sizeof(buffer), client->input) == NULL) {
        fclose(client->input);
        fclose(client->output);
        free(client->name);
        free(client);
        return NULL;
    }

    // remove newline char
    len = strlen(buffer);
    if (len > 0 && buffer[len-1] == '\n') {
        buffer[len-1] = '\0';
    }
    strcpy(room_name, buffer);

    // find requested chatroom
    pthread_mutex_lock(rooms_mutex);
    requested_room = jrb_find_str(chat_rooms, room_name);
    pthread_mutex_unlock(rooms_mutex);

    // set room for client
    room = (Chatroom *) requested_room->val.v;
    client->room = room;
    
    // Add client to chat room client list
    pthread_mutex_lock(room->mutex);
    dll_append(room->client_list, new_jval_v(client));
    pthread_mutex_unlock(room->mutex);
    
    // Print to users that a new client has joined
    char *intro_message = (char *) malloc(strlen(client->name) + 20);
    strcpy(intro_message, client->name);
    strcat(intro_message, " has joined\n");
    pthread_mutex_lock(room->mutex);
    dll_append(room->message_list, new_jval_s(intro_message));
    pthread_cond_signal(room->cond);
    pthread_mutex_unlock(room->mutex);
    
    // Loop to read messages from client
    while (client->active) {
      // after client has joined , if fgets() reads EOF they've disconnected
        if (fgets(buffer, sizeof(buffer), client->input) == NULL) {
            break;  
        }
        
        // Create and add message to room's message list and signal the room condition variable
        char *message = (char *) malloc(strlen(client->name) + strlen(buffer) + 10);
        strcpy(message, client->name);
        strcat(message, ": ");
        strcat(message, buffer);
        
        pthread_mutex_lock(room->mutex);
        dll_append(room->message_list, new_jval_s(strdup(message)));
        pthread_cond_signal(room->cond);
        pthread_mutex_unlock(room->mutex);
        
        free(message);
    }
    
    // client has disconnected
    pthread_mutex_lock(room->mutex);

    // remove client from client list
    dll_traverse(tmp_node, room->client_list) {
        if (tmp_node->val.v == client) {
            dll_delete_node(tmp_node);
            break;
        }
    }

    // print client has left to others
    char *exit_message = (char *) malloc(strlen(client->name) + 20);
    strcpy(exit_message, client->name);
    strcat(exit_message, " has left\n");
    dll_append(room->message_list, new_jval_s(exit_message));
    pthread_cond_signal(room->cond);
    pthread_mutex_unlock(room->mutex);

    // check if the output buffer is still open and if the chat room thread is not currently trying to write to it
    if (client->output != NULL) {
        fclose(client->output);
        client->output = NULL;
    }
    
    // free client
    free(client->name);
    free(client);

}

// Chat room thread function
void *chatroom_thread(void *arg) {
    Chatroom *room = (Chatroom *) arg;
    Dllist tmp, client_tmp;
    char *message;
    Client *client;
    
    while (1) {
        pthread_mutex_lock(room->mutex);
        
        // Block on cindition variable until there is a message to send
        while (dll_empty(room->message_list)) {
            pthread_cond_wait(room->cond, room->mutex);
        }
        
        // Traverse all messages when condition variable is signaled
        while (!dll_empty(room->message_list)) {
            tmp = dll_first(room->message_list);
            message = tmp->val.s;
            
            // Traverse all clients in the room and send the message
            dll_traverse(client_tmp, room->client_list) {
                client = (Client *) client_tmp->val.v;
                if (client->active) {
                  // if there is a problem with fputs() or fflush(), remove client from list and close ouput buffer
                    if (fputs(message, client->output) == EOF || fflush(client->output) != 0) {
                        client->active = 0;
                        fclose(client->output);
                        client->output = NULL;
                        dll_delete_node(client_tmp);
                    }
                }
            }
            
            // Remove message from list
            dll_delete_node(tmp);
            free(message);
        }
        
        pthread_mutex_unlock(room->mutex);
    }
}

int main(int argc, char **argv) {
    JRB room_tmp;
    if (argc < 3) {
        fprintf(stderr, "Usage: ./chat_server port chatrooms... \n");
        exit(1);
    }

    int port = atoi(argv[1]);
    
    // global variables
    chat_rooms = make_jrb();
    rooms_mutex = new_mutex();
    
    // create all chatrooms
    for (int i = 2; i < argc; i++) {
        Chatroom *room = (Chatroom *) malloc(sizeof(Chatroom));
        room->name = strdup(argv[i]);
        room->mutex = new_mutex();
        room->cond = new_cond();
        room->client_list = new_dllist();
        room->message_list = new_dllist();
        pthread_mutex_lock(rooms_mutex);
        
        // Add to chat room tree
        jrb_insert_str(chat_rooms, room->name, new_jval_v(room));
        pthread_mutex_unlock(rooms_mutex);
        
        // Create thread for chat room
        if (pthread_create(&room->thread_id, NULL, chatroom_thread, room) != 0) {
            perror("pthread_create for chat room");
            exit(1);
        }
    }
    
    // Create server socket
    int server_socket = serve_socket(port);
    if (server_socket < 0) {
        perror("serve_socket");
        exit(1);
    }
    
    // Running while loop waiting for clients
    while (1) {
        int client_fd = accept_connection(server_socket);
        if (client_fd < 0) {
            perror("accept_connection");
            continue;
        }
        
        // Create a new client and initialize
        Client *client = (Client *) malloc(sizeof(Client));
        client->input = fdopen(client_fd, "r");
        client->output = fdopen(client_fd, "w");
        client->active = 1;
        
        // Create new client thread and error check
        if (pthread_create(&client->thread_id, NULL, client_thread, client) != 0) {
            perror("pthread_create for client");
            fclose(client->input);
            fclose(client->output);
            free(client);
            continue;
        }

        // detach the thread so it can clean up resources when it exits
        pthread_detach(client->thread_id);  
    }

    // Clean up
    close(server_socket);
    pthread_mutex_destroy(rooms_mutex);
    free(rooms_mutex);
    jrb_traverse(room_tmp, chat_rooms) {
        Chatroom *room = (Chatroom *) room_tmp->val.v;
        free(room->name);
        pthread_mutex_destroy(room->mutex);
        free(room->mutex);
        pthread_cond_destroy(room->cond);
        free(room->cond);
        free(room);
    }
}
