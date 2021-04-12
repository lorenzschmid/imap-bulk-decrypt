import imaplib
from email.parser import BytesParser
from email.policy import default
from email.utils import parsedate_tz, mktime_tz
import re


class ImapException(Exception):
    pass


class NoConnection(ImapException):
    pass


class InvalidPath(ImapException):
    pass


class InvalidMsgId(ImapException):
    pass


class OperationFailed(ImapException):
    pass


class Imap:
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

        self._imap = None
        self._path = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()

    def open(self):
        self._imap = imaplib.IMAP4_SSL(self.host)
        ok, res = self._imap.login(self.user, self.password)
        if ok != "OK":
            raise NoConnection(res[0].decode())

    def close(self):
        if self._path is not None:
            self.expunge()
            self._imap.close()
        self._imap.logout()

    @property
    def imap(self):
        if not self._imap:
            raise NoConnection()
        else:
            return self._imap

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self.cd(value)

    def _require_path(func):
        def wrapper(*args):
            if not args[0].path:
                raise InvalidPath("No root path selected.")
            return func(*args)

        return wrapper

    def cd(self, path):
        ok, res = self.imap.select(path)
        if ok != "OK":
            raise InvalidPath(res[0].decode())

        self._path = path

    def ls(self):
        if not self.path:
            folders = self.imap.list()[1]
        else:
            folders = self.imap.list(self.path)[1]

        folders = [re.sub(r'^\([^)]+\)\s"."\s', "", f.decode()) for f in folders]

        # Remove current path
        if self.path and self.path in folders:
            folders.remove(self.path)

        return folders

    @_require_path
    def mkdir(self, name):
        ok, res = self.imap.create(name)
        if ok != "OK":
            raise InvalidPath(res[0].decode())

    @_require_path
    def _search_folder(self):
        # search for PGP/MIME messages
        ok, res = self.imap.search(None, '(HEADER Content-Type "pgp-encrypted")')
        if ok == "OK":
            mime = res[0].decode().split()
        else:
            mime = []

        # search for inline messages (boundaries in body)
        ok, res = self.imap.search(None, '(BODY "-----BEGIN PGP MESSAGE-----")')
        if ok == "OK":
            inline = res[0].decode().split()
        else:
            inline = []

        return (mime, inline)

    @_require_path
    def search(self, recursive=True):
        uids = []
        path = self.path

        # Search current folder
        mime, inline = self._search_folder()
        if mime or inline:
            uids.append({"path": path, "mime": mime, "inline": inline})

        if recursive:
            # Search recursively by selecting each subfolder
            dirs = self.ls()
            for d in dirs:
                self.cd(d)
                uids_sub = self.search()
                if uids_sub:
                    uids += uids_sub

            # Select back original folder
            self.cd(path)

        # Remove duplicates
        uids = list({u["path"]: u for u in uids}.values())

        return uids

    @_require_path
    def get_msg(self, uid):
        # Get message flags
        ok, response = self.imap.fetch(uid.encode(), "(FLAGS)")
        if ok != "OK":
            raise InvalidMsgId("Could not fetch flags for message {}.".format(uid))
        elif response:
            s = re.search(r"FLAGS \(([^\)]*)\)", response[0].decode())
            if s:
                flags = s.group(1).split(" ")
                flags = list(filter(None, flags))
        if not flags:
            flags = None

        # Get message
        ok, response = self.imap.fetch(uid.encode(), "(RFC822)")
        if ok != "OK":
            raise InvalidMsgId("Could not fetch message {}.".format(uid))
        else:
            msg = BytesParser(policy=default).parsebytes(response[0][1])

        return (msg, flags)

    @_require_path
    def add_msg(self, msg, flags=None):
        # Prepare flags
        if flags:
            flag_str = " ".join(flags)
        else:
            flag_str = None

        # Get timestamp from message
        date_str = msg.get("date")
        date_tuple = parsedate_tz(date_str)
        ts_utc = mktime_tz(date_tuple)
        imap_date = imaplib.Time2Internaldate(ts_utc)

        msg_bytes = msg.as_bytes()

        # Upload message
        ok, _ = self.imap.append(self.path, flag_str, imap_date, msg_bytes)
        if ok != "OK":
            raise OperationFailed("Could not add message.")

    @_require_path
    def rm_msg(self, uid):
        # Mark message as to be deleted
        ok, _ = self.imap.store(uid, "+FLAGS", "\\Deleted")
        if ok != "OK":
            raise OperationFailed("Could not delete message {}.".format(uid))

    @_require_path
    def expunge(self):
        # Delete marked messages
        self.imap.expunge()

    @_require_path
    def cp_msg(self, uid, path):
        ok, _ = self.imap.copy(uid, path)
        if ok != "OK":
            raise OperationFailed("Could not copy message {} to {}.".format(uid, path))

    def mv_msg(self, uid, path):
        self.cp_msg(uid, path)
        self.rm_msg(uid)
