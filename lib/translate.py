from email.parser import BytesParser
from email.policy import default
import gnupg
import re


class TranslateException(Exception):
    pass


class NotEncrypted(TranslateException):
    pass


class MultipartEncrypted(TranslateException):
    pass


class GpgError(TranslateException):
    pass


TAG_BEGIN = "-----BEGIN PGP MESSAGE-----"
NO_SECKEY = "decryption failed: No secret key"


def decrypt(gpg, msg_str):
    # Add argument to decrypt messages with expired keys
    d = gpg.decrypt(msg_str, extra_args=["--ignore-mdc-error"])

    if (d.ok or (d.status == "signature valid" and d.valid)) and d.data != "":
        return d.data

    else:
        if NO_SECKEY in d.stderr:
            raise GpgError("No secret key available.")
        else:
            raise GpgError(
                "Could not decrypt message string. GPG exited " + f'with "{d.status}".'
            )


def translate(gpg, msg):
    if msg.is_multipart():
        # PGP/MIME
        if "encrypted" in msg.get("Content-Type"):
            # Get encrypted content
            p = next(p for i, p in enumerate(msg.iter_parts()) if i == 1)
            content = p.get_content()

            # Decrypt content
            d_content = decrypt(gpg, content)

            # Create new message with decrypted content
            new_msg = BytesParser(policy=default).parsebytes(d_content)

            # Copy headers from old message
            for h_name, h_value in msg.items():
                try:
                    new_msg.add_header(h_name, h_value)
                except ValueError:
                    # Skip existing headers, such as Content-Type
                    continue

            return new_msg

        # Verify if one part of multipart message is encrypted
        else:
            raise MultipartEncrypted(
                "Multipart Message is not of type PGP/MIME and thus not supported."
            )

    # PGP/Inline
    elif re.search(rf"^{TAG_BEGIN}", msg.get_content(), flags=re.MULTILINE):
        content = msg.get_content()

        # Decrypt content
        d_content = decrypt(gpg, content)

        # Decode message (bytes to str)
        m = re.search(r"Charset: ([^\s]*)", content)
        if m:
            encoding = m.group(1)
        else:
            # Default to utf-8
            encoding = "utf-8"

        try:
            d_content = d_content.decode(encoding)
        except LookupError:
            raise GpgError("Unknown encoding: {}".format(encoding))

        # Replace content
        msg.set_content(d_content)

        return msg

    else:
        raise NotEncrypted("Message is not encrypted.")


def get_gpg():
    return gnupg.GPG(use_agent=True)
