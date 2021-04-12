import mailbox


class MailboxException(Exception):
    pass


class InvalidFolder(MailboxException):
    pass


class MsgEncodingError(MailboxException):
    pass


class Mailbox:
    def __init__(self, dirname):
        self.dirname = dirname

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()

    def open(self):
        self.root_dir = mailbox.Maildir(self.dirname)
        self.curr_dir = mailbox.Maildir(self.dirname)
        self._path = None

    def close(self):
        pass

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self.cd(value)

    def cd(self, path, relative=False, mkdir=False):
        path = path.replace('"', "")
        dirs = path.split("/")

        if not relative:
            # Start from root
            self.curr_dir = self.root_dir

        curr_dir = self.curr_dir
        for d in dirs:
            try:
                new_dir = curr_dir.get_folder(d)
            except mailbox.NoSuchMailboxError:
                if mkdir:
                    new_dir = curr_dir.add_folder(d)
                else:
                    raise InvalidFolder()
            curr_dir = new_dir

        self.curr_dir = curr_dir
        self._path = path

    def mkdir(self, path, relative=False):
        self.cd(path, relative, True)

    def add_msg(self, msg):
        self.curr_dir.add(msg)
