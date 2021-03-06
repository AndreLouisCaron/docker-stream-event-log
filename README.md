# docker-stream-event-log: stream a (secondary) event log

This is a sketch for a solution to stream the event log generated by an
application running inside a Docker container.  Of course, application logs
should be written to standard output (or standard error), but every so often,
you have applications with multiple data streams that simply insist on writing
to files.

## Goals

The solution must meet a few simple criteria:

- minimize changes to the source application;
- mimic a solution frequently used by well-known application (e.g. HTTP access
  log in popular web servers);
- minimize Do-It-Yourself solutions;
- support multiple destinations (minimum: ElasticSearch); and
- support running as a self-contained Kubernetes `Pod` (scheduled via a
  `Deployment` to run many instances of the application generating the data
  stream).

## Solution

The various problems to solve and the sketch of the solution are presented
below.  The demo is presented as a Docker Compose file because it's easier to
test and run with fewer requirements (access to any Docke daemon will do), but
it should be straightforward to port this to a Kubernetes `Deployment`.

### Streaming the file

The first (and most obvious) problem to solve is streaming the data file.
There are many solutions for tailing log files, with various trade-offs.  In
this case, we will use [fluent-bit](https://github.com/fluent/fluent-bit)
because it's already available on Docker Hub, it's simple to configure and it's
designed to be super light-weight.

### Limiting the log file size

If the application generates data and is left running for extended periods of
time, its log file will grow very large and the container will eventually run
out of disk space.

This can be solved by rotating the log file once it reaches a given size limit.

Of course, the application can implement log file rotation, but there is more
ubiquitous tool for this: [logrotate](https://github.com/logrotate/logrotate).
This solution is already used by many Linux systems and is frequently used to
control the size of log files in popular web servers.

The setup is easy enough:

- configure `logrotate` to rotate the log file once it has execeeded a certain
  size;
- configure `logrotate` to send a signal (e.g. `SIGHUP`) to the application,
  informing it that the log file has been renamed and that it should close and
  re-open its log file;
- run `logrotate` on a schedule (e.g. using `crond`).

This requires a single change to our application: it must close and re-open its
log file when it receives `SIGHUP`.

### Stream aggregation

We want to use a ``Deployment`` to run multiple instances of this application.
When you run enough of these instances, the number of inbound connections to
the final data source (e.g. ElasticSearch) becomes an issue.  To solve this, we
can run a log aggregation service like [FluentD](https://www.fluentd.org/).

However, a central FluentD service cannot tail the log files inside each of our
pods.  For this, we can run [fluent-bit](https://github.com/fluent/fluent-bit)
as a Kubernetes sidecar, which can simply forward all the data to FluentD.

**Note**: stream aggregation is not demonstrated in this project.  Forwarding
  to FluentD (and then to ElasticSearch) is left as an exercise to the reaer.
