# PRASM

Meet practicality of NASM assembler with beauty of presentations!

To use it you need:

- [NASM](https://www.nasm.us/)
- WYSIWYG presentation editor supporting OpenDocumentFormat like [LibreOffice](https://www.libreoffice.org)

See examples in [examples/](./examples/)!

- [examples/exit_42.odp](examples/exit_42.odp) simply calls `exit(42)` syscall
- [examples/hello_world.odp](examples/hello_world.odp) prints "hello, world!" to standard output
- [examples/pics.odp](examples/pics.odp) outputs one of the stored in presentation pictures to the path provided by command line arguments

```
$ python prasm.py --run examples/exit_42.odp
$ echo $?
42
$ python prasm.py --run examples/hello_world.odp
hello, world!
$ python prasm.py --run examples/pics.odp cat-or-dog.jpg
$ xdg-open cat-or-dog.jpg
```

## How to use it?

To write in this language create presentation in Open Document Format (I tested with [LibreOffice](https://www.libreoffice.org/)). First page is considered title page and will not be included. The following pages create new NASM assembly file where:

- Slide title is considered to be content's label. Following pages with the same slide title create one code piece
- Text nodes in slide are meant for NASM assembly
- Shapes with text or images are included as binary blobs of data.

Additionaly language provides standard library known as `prelude`, which contains Linux system calls numbers and some common flags for file creation and IO.

After presentation creation transpile it into NASM assembly using `prasm.py` script. Assembling using nasm assembler is done by script.

```console
$ ./prasm.py examples/exit_42.odp
$ ./examples/exit_42.out
$ echo $?
42
```

## Why?

[Lang Jam3 (#0003)](https://github.com/langjam/jam0003) theme is __Beautiful Assembly__. Assembly is the beautiful but we can improve them by including cat pictures! And one of the most common form of mixing text with pictures and color is presentations!
