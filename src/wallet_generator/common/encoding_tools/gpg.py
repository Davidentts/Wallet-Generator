import os
import re
import subprocess
from pathlib import Path

from wallet_generator.common.schemas.keys import (
    UID,
    SubKey,
    BaseKey,
    PublicKey,
    SecretKey,
)


class GPGError(RuntimeError):
    pass


class GPG:
    def __init__(self, gpg_binary: str = "gpg", preload_keys: bool = True):
        self.gpg_binary = gpg_binary

        self.public_keys: list[PublicKey] = []
        self.private_keys: list[SecretKey] = []

        if preload_keys:
            self.reload_keys()

    def reload_keys(self) -> None:
        self.public_keys = self._list_keys(
            command=["--list-keys"],
            key_cls=PublicKey,
        )
        self.private_keys = self._list_keys(
            command=["--list-secret-keys"],
            key_cls=SecretKey,
        )

    def _list_keys(
        self,
        *,
        command: list[str],
        key_cls: type[BaseKey],  # PublicKey or SecretKey
    ) -> list[BaseKey]:

        output = self._run(command)

        keys: list[key_cls] = []
        current_key: key_cls | None = None

        pub_re = re.compile(
            r"^pub\s+(\S+)/0x([0-9A-F]+)\s+(\d{4}-\d{2}-\d{2})\s+\[([A-Z]+)]"
        )
        sec_re = re.compile(
            r"^sec\s+(\S+)/0x([0-9A-F]+)\s+(\d{4}-\d{2}-\d{2})\s+\[([A-Z]+)]"
        )
        sub_re = re.compile(
            r"^sub\s+(\S+)/0x([0-9A-F]+)\s+(\d{4}-\d{2}-\d{2})\s+\[([A-Z]+)]"
        )
        ssb_re = re.compile(
            r"^ssb\s+(\S+)/0x([0-9A-F]+)\s+(\d{4}-\d{2}-\d{2})\s+\[([A-Z]+)]"
        )
        uid_re = re.compile(r"^uid\s+\[\s*(.*?)\s*]\s*(.*?)\s*<(.*?)>")

        for line in output.splitlines():
            stripped = line.strip()

            # Skip "[keyboxd]" and "---------"
            if not stripped or stripped.startswith("-") or stripped.startswith("["):
                continue

            # ---------- PUBLIC KEY ----------
            m_pub = pub_re.match(stripped)
            if m_pub:
                algo, keyid, created, caps = m_pub.groups()
                # Save the previous key if there was one
                if current_key is not None:
                    keys.append(current_key)

                current_key = PublicKey(
                    algo=algo,
                    keyid=keyid,
                    created=created,
                    caps=list(caps),
                    fingerprint="",
                )
                continue

            # ---------- SECRET KEY ----------
            m_sec = sec_re.match(stripped)
            if m_sec:
                algo, keyid, created, caps = m_sec.groups()
                if current_key is not None:
                    keys.append(current_key)

                current_key = SecretKey(
                    algo=algo,
                    keyid=keyid,
                    created=created,
                    caps=list(caps),
                    fingerprint="",
                )
                continue

            # ---------- FINGERPRINT ----------
            if current_key is not None and re.fullmatch(r"[0-9A-F]{40}", stripped):
                current_key.fingerprint = stripped
                continue

            # ---------- UID ----------
            m_uid = uid_re.match(stripped)
            if m_uid and current_key is not None:
                validity, name, email = m_uid.groups()
                current_key.uids.append(
                    UID(
                        validity=validity,
                        name=name,
                        email=email,
                    )
                )
                continue

            # ---------- SUBKEY (PUBLIC) OR SECRET SUBKEY (PRIVATE) ----------
            m_ssb = ssb_re.match(stripped)
            m_sub = sub_re.match(stripped)
            m_ssub = m_ssb if m_ssb else m_sub
            if m_ssub:
                algo, keyid, created, caps = m_ssub.groups()
                current_key.ssub.append(
                    SubKey(
                        algo=algo,
                        keyid=keyid,
                        created=created,
                        caps=list(caps),
                    )
                )
                continue

        # Last key
        if current_key is not None:
            keys.append(current_key)
        return keys

    def _run(
        self,
        args: list[str],
        input_data: str | None = None,
        check: bool = False,
    ) -> str:
        try:
            result = subprocess.run(
                [self.gpg_binary] + args,
                check=check,
                capture_output=True,
                text=True,
                input=input_data,
            )
        except FileNotFoundError as e:
            raise GPGError(f"gpg not found: {self.gpg_binary}") from e

        if result.returncode != 0:
            raise GPGError(
                f"gpg завершился с кодом {result.returncode}: {result.stderr.strip()}"
            )

        return result.stdout

    def decrypt_from_file(self, file: Path) -> str:
        args = ["--decrypt", file]
        decrypted = self._run(args)
        return decrypted

    def encrypt_message(
        self,
        message: str,
        recipient: PublicKey,
        *,
        armor: bool = True,
        always_trust: bool = False,
    ) -> str:
        """
        Encrypt the message for the specified recipient.

        recipient — recipient's public key.
        armor=True - ASCII format.
        always_trust=True — do not ask about trust in the key.
        """
        args: list[str] = []

        if always_trust:
            args.extend(["--trust-model", "always"])

        if armor:
            args.append("--armor")

        args += [
            "--encrypt",
            "--no-throw-keyids",
            "--recipient",
            recipient.fingerprint,
        ]

        ciphertext = self._run(args, input_data=message)
        return ciphertext

    def _run_popen(
        self,
        args: list[str],
        message_bytes: bytes,
        password: bytes,
    ):
        r, w = os.pipe()
        try:
            with subprocess.Popen(
                [self.gpg_binary] + args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                pass_fds=(r,),
            ) as proc:
                os.write(w, password)
                os.close(w)

                ciphertext, stderr = proc.communicate(message_bytes)

                if proc.returncode != 0:
                    raise GPGError(
                        f"gpg failed with code {proc.returncode}: "
                        f"{stderr.decode('utf-8', errors='ignore')}"
                    )

                return ciphertext.decode("utf-8")
        finally:
            try:
                os.close(r)
                os.close(w)
            except OSError:
                pass

    def encrypt_message_symmetric(self, message: str, password: str):

        message = message.encode("utf-8")
        password = password.encode("utf-8")

        args = [
            "--pinentry-mode",
            "loopback",
            "--passphrase-fd",
            "3",
            "-c",
            "-a",
        ]

        ciphertext = self._run_popen(args, message, password)
        return ciphertext

    def encrypt_file(
        self,
        file: Path,
        recipient: PublicKey,
        *,
        armor: bool = True,
        always_trust: bool = False,
    ) -> None:
        """
        Encrypt the message for the specified recipient.

        recipient — recipient's public key.
        armor=True - ASCII format.
        always_trust=True — do not ask about trust in the key.
        """
        args: list[str] = []

        if always_trust:
            args.extend(["--trust-model", "always"])

        if armor:
            args.append("--armor")

        args += [
            "--encrypt",
            "--no-throw-keyids",
            "--recipient",
            recipient.fingerprint,
            file,
        ]

        self._run(args)

    def encrypt_file_symmetric(
        self,
        file: Path,
        password: str,
    ) -> None:
        args = [
            "--pinentry-mode",
            "loopback",
            "--passphrase-fd",
            "0",
            "-c",
            file,
        ]
        self._run(args, input_data=password)
