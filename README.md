# Distributed Auction and Bidding System

A Python-based client-server auction application demonstrating TCP socket communication, concurrent client handling, bid validation, shared auction state, and real-time status updates.

## Overview

The system consists of a TCP server and GUI clients. Multiple clients can connect to the server and submit bids. The server coordinates shared auction state, validates incoming bids, broadcasts accepted highest bids, maintains bid history, and ends an auction based on its configured duration/inactivity rules.

## Architecture

```text
+------------------+       TCP Socket       +------------------+
|  Client 1 (GUI)  | <--------------------> |                  |
+------------------+                         |                  |
                                             |  Auction Server  |
+------------------+       TCP Socket       |                  |
|  Client 2 (GUI)  | <--------------------> |                  |
+------------------+                         +------------------+
```

## Key Concepts

- TCP socket-based client-server communication
- Multi-client concurrency using Python threads
- Shared state synchronization using a thread lock
- Highest-bid validation and bid history
- Broadcast of auction updates to connected clients
- Configurable auction duration and inactivity timeout
- Tkinter GUI for both server and clients

## Repository Structure

```text
client.py
server.py
README.md
```

## Requirements

- Python 3.x
- Tkinter (normally included with standard Python installations)
- Windows for the current server implementation because it uses `winsound` for bid notifications

## Running

### Start the server

```bash
python server.py
```

Use the server GUI to start the server and then start an auction by providing its duration and inactivity timeout.

### Start a client

In one or more additional terminals:

```bash
python client.py
```

Enter a bidder name and numeric bid and select **Place Bid**.

For multiple machines, change `SERVER_IP` in `client.py` to the server machine's local network IP and ensure TCP port `5000` is reachable.

## Implementation Notes

The server protects updates to the shared highest-bid state with a threading lock. Accepted bids update the auction state and are broadcast to connected clients. The client uses a background receiver thread so incoming server messages can update the GUI without blocking bid submission.

## Limitations / Future Improvements

This is a course-project implementation rather than a production financial auction system. Potential extensions include persistent storage, authentication, structured message formats, stronger exception handling, client cleanup, server-side validation, configurable logging, and deployment as separate service processes.
