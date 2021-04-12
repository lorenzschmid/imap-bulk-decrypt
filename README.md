# imap-bulk-decrypt

Bulk-decrypt GPG encrypted messages via IMAP

```
usage: imap-bulk-decrypt [-h] [-c CONFIG] [--server SERVER] [-p PATH] [-u UID] [-s] [-r REMOTE] [-l LOCAL LOCAL] [-f]
                         [-R] [-m] [-d LOGGING_LEVEL]

Bulk-decrypt GPG encrypted messages via IMAP.

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        IMAP server configuration file
  --server SERVER       Server name to choose from configuration file
  -p PATH, --path PATH  Path on IMAP server to operate on
  -u UID, --uid UID     Act on single message for given ID in path
  -s, --search          Search for encrypted messages in path and print IDs
  -r REMOTE, --remote REMOTE
                        Remote mode: "decrypt" to overwrite remote messages with decrypted message, "print" to print header of found messages
  -l LOCAL LOCAL, --local LOCAL LOCAL
                        Local mode: "decrypt" to store remote messages decrypted, "backup" to store remote messages as they are, followed by path to store Maildir
  -f, --force           Overwrite messages on IMAP server without confirmation
  -R, --recursive       Operate not only on path but also its subitems
  -m, --mark-only       Mark messages only as to be deleted instead of deleting them
  -d LOGGING_LEVEL, --logging-level LOGGING_LEVEL
                        Set output logging level (Default: INFO)
```
