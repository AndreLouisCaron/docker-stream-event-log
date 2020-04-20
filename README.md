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
  log in popular web servers); and
- minimize Do-It-Yourself solutions.