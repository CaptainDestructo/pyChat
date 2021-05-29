#!/usr/bin/env python

import asyncio
import websockets


clients = {}


@asyncio.coroutine
def client_handler(websocket, path):
    print("New client", websocket)
    print(" ({} existing clients)".format(len(clients)))

    # The first line from the client is the name
    name = yield from websocket.recv()
    yield from websocket.send("Welcome to websocket-chat, {}\n".format(name))
    yield from websocket.send(
        "There are {} other users connected: {}\n".format(
            len(clients), list(clients.values())
        )
    )
    clients[websocket] = name
    for client, _ in clients.items():
        yield from client.send(name + " has joined the chat\n")

    # Handle messages from this client
    while True:
        message = yield from websocket.recv()
        if message is None:
            their_name = clients[websocket]
            del clients[websocket]
            print("Client closed connection", websocket)
            for client, _ in clients.items():
                yield from client.send(their_name + " has left the chat\n")
            break

        # Send message to all clients
        for client, _ in clients.items():
            yield from client.send("{}: {}\n".format(name, message))


start_server = websockets.serve(client_handler, "localhost", 12345)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()