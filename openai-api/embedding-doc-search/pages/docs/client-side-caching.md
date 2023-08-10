
## There are two hard problems in computer science...

A problem with the above pattern is how to invalidate the information that
the application is holding, in order to avoid presenting stale data to the
user. For example after the application above locally cached the information
for user:1234, Alice may update her username to Flora. Yet the application
may continue to serve the old username for user:1234.

Sometimes, depending on the exact application we are modeling, this isn't a
big deal, so the client will just use a fixed maximum "time to live" for the
cached information. Once a given amount of time has elapsed, the information
will no longer be considered valid. More complex patterns, when using Redis,
leverage the Pub/Sub system in order to send invalidation messages to
listening clients. This can be made to work but is tricky and costly from
the point of view of the bandwidth used, because often such patterns involve
sending the invalidation messages to every client in the application, even
if certain clients may not have any copy of the invalidated data. Moreover
every application query altering the data requires to use the `PUBLISH`
command, costing the database more CPU time to process this command.

Regardless of what schema is used, there is a simple fact: many very large
applications implement some form of client-side caching, because it is the
next logical step to having a fast store or a fast cache server. For this
reason Redis 6 implements direct support for client-side caching, in order
to make this pattern much simpler to implement, more accessible, reliable,
and efficient.

## The Redis implementation of client-side caching

The Redis client-side caching support is called _Tracking_, and has two modes:

* In the default mode, the server remembers what keys a given client accessed, and sends invalidation messages when the same keys are modified. This costs memory in the server side, but sends invalidation messages only for the set of keys that the client might have in memory.
* In the _broadcasting_ mode, the server does not attempt to remember what keys a given client accessed, so this mode costs no memory at all in the server side. Instead clients subscribe to key prefixes such as `object:` or `user:`, and receive a notification message every time a key matching a subscribed prefix is touched.

To recap, for now let's forget for a moment about the broadcasting mode, to
focus on the first mode. We'll describe broadcasting in more detail later.

1. Clients can enable tracking if they want. Connections start without tracking enabled.
2. When tracking is enabled, the server remembers what keys each client requested during the connection lifetime (by sending read commands about such keys).
3. When a key is modified by some client, or is evicted because it has an associated expire time, or evicted because of a _maxmemory_ policy, all the clients with tracking enabled that may have the key cached, are notified with an _invalidation message_.
4. When clients receive invalidation messages, they are required to remove the corresponding keys, in order to avoid serving stale data.

This is an example of the protocol:

* Client 1 `->` Server: CLIENT TRACKING ON
* Client 1 `->` Server: GET foo
* (The server remembers that Client 1 may have the key "foo" cached)
* (Client 1 may remember the value of "foo" inside its local memory)
* Client 2 `->` Server: SET foo SomeOtherValue
* Server `->` Client 1: INVALIDATE "foo"

This looks great superficially, but if you imagine 10k connected clients all
asking for millions of keys over long living connection, the server ends up
storing too much information. For this reason Redis uses two key ideas in
order to limit the amount of memory used server-side and the CPU cost of
handling the data structures implementing the feature:

* The server remembers the list of clients that may have cached a given key in a single global table. This table is called the **Invalidation Table**. The invalidation table can contain a maximum number of entries. If a new key is inserted, the server may evict an older entry by pretending that such key was modified (even if it was not), and sending an invalidation message to the clients. Doing so, it can reclaim the memory used for this key, even if this will force the clients having a local copy of the key to evict it.
* Inside the invalidation table we don't really need to store pointers to clients' structures, that would force a garbage collection procedure when the client disconnects: instead what we do is just store client IDs (each Redis client has a unique numerical ID). If a client disconnects, the information will be incrementally garbage collected as caching slots are invalidated.
* There is a single keys namespace, not divided by database numbers. So if a client is caching the key `foo` in database 2, and some other client changes the value of the key `foo` in database 3, an invalidation message will still be sent. This way we can ignore database numbers reducing both the memory usage and the implementation complexity.
