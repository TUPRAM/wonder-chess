"""Ask the owner for the Meshy API key and store it encrypted for this Windows user, outside the project.

Writes the same file as support/tools/meshy/Set-MeshyKey.ps1, so every existing tool can read it. The key is
never printed or logged, and no generation is submitted here.
"""
import ctypes
import ctypes.wintypes
import os
import tkinter
from pathlib import Path
from tkinter import messagebox

KEY_FILE = Path(os.environ["LOCALAPPDATA"]) / "WonderChess/credentials/meshy-api-key.dpapi"


class Blob(ctypes.Structure):
    _fields_ = [("size", ctypes.wintypes.DWORD), ("data", ctypes.POINTER(ctypes.c_char))]


def protect(text):
    raw = text.encode("utf-16-le")
    source = Blob(len(raw), ctypes.cast(ctypes.create_string_buffer(raw, len(raw)), ctypes.POINTER(ctypes.c_char)))
    target = Blob()
    if not ctypes.windll.crypt32.CryptProtectData(ctypes.byref(source), None, None, None, None, 0,
                                                  ctypes.byref(target)):
        raise OSError("Windows could not encrypt the key")
    try:
        return ctypes.string_at(target.data, target.size).hex()
    finally:
        ctypes.windll.kernel32.LocalFree(target.data)


def main():
    window = tkinter.Tk()
    window.title("Wonder Chess - Meshy API key")
    window.attributes("-topmost", True)
    tkinter.Label(window, justify="left", padx=14, pady=10, text=(
        "Paste your Meshy API key below. It is encrypted for your Windows user,\n"
        "kept outside the project and never shown. Nothing is generated here.")).pack()
    entry = tkinter.Entry(window, show="*", width=64)
    entry.pack(padx=14)
    entry.focus_set()

    def store(_event=None):
        key = entry.get().strip()
        if not key:
            return
        KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
        KEY_FILE.write_text(protect(key) + "\n", encoding="ascii")
        entry.delete(0, "end")
        messagebox.showinfo("Wonder Chess", "The key is stored. You can close this window.")
        window.destroy()

    tkinter.Button(window, text="Save key locally", command=store).pack(pady=12)
    window.bind("<Return>", store)
    window.mainloop()


if __name__ == "__main__":
    main()
