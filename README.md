# File Backup

## About

Command line application to copy the folder content from one location to another.

Location is not restricted to the local file system as there is an ability to choose both input and output handlers.

> All of the handlers can be used in an arbitrary order.

Application has the following handlers:

- "vanila" file system;
- remote sftp server;
- google drive.

> SFTP handler requires server configurations (IP address, key file location), GDrive handler requires credentials for the V3 API.

* * *

## Used libraries

- `googleapiclient`
- `pysftp`
- `os`

`LocalHandler` mainly uses built-in `os` library as it provides tools for the folder creation, file system inromation retriving.
`SFTPHandler` uses `pysftp` library that is very similar to the `os` library
`GDriveHandler` uses [GoogleDrive V3 API](https://developers.google.com/drive/api/quickstart/quickstarts-overview).

* * *

## Installation

```sh
git clone https://github.com/Denis-Source/file_backup.git
```

```sh
python3 -m venv env/
source env/bin/activate
```

```sh
python main.py -i {input_folder} -o {output_folder}
```

* * *

## Showcase

The console applicaiton has the following signature:

```sh
usage: main.py [-h] [-ih INPUT_HANDLER] [-oh OUTPUT_HANDLER] [-i INPUT] -o OUTPUT [-v]

File Backup command line App
optional arguments:
  -h, --help                 show this help message and exit
  -ih, --input_handler       type of a handler as an input
  -oh, --output_handler				type of a handler as an output
  -i, --input                input location
  -o, --output               output location
  -v, --validation           use validators defined in the configs
```

> All of the exapmles below were provided using [WSL](https://docs.microsoft.com/ru-ru/windows/wsl/install) to avoid mixing of UNIX and Windows file system path formats.

***

### Local Handler
Considering we have the following file tree structure:
```sh
~/samples$ tree
.
├── BuzzBuzz_edited.wav
├── SX_Door_origin.wav
├── SX_Phone_origin.wav
└── edited
    └── Wow_Edited.wav

1 directory, 4 files
```

> By Default if input or output handlers are not specified, the local handler will be used

We can copy the folder content from one location to another, using `-i` and `-o` keys:
```sh
python3 main.py -i ~/samples/ -o /mnt/c/file_backup/samples
```

The folders content were copied to the specified output folder:
```sh
tree /mnt/c/file_backup/samples/
/mnt/c/file_backup/samples/
├── BuzzBuzz_edited.wav
├── SX_Door_origin.wav
├── SX_Phone_origin.wav
└── edited
    └── Wow_Edited.wav

1 directory, 4 files
```

The logging output:
```sh
2022-08-27 17:13:04,560 INFO    app             Backuping files from /home/den/samples/ using local handler to /mnt/c/file_backup/samples using local handler not using validators
2022-08-27 17:13:04,560 INFO    local           Got information about a folder at /home/den/samples/
2022-08-27 17:13:04,561 INFO    local           Got information about a file at /home/den/samples//SX_Door_origin.wav
2022-08-27 17:13:04,561 INFO    local           Got information about a folder at /home/den/samples//edited
2022-08-27 17:13:04,561 INFO    local           Got information about a file at /home/den/samples//SX_Phone_origin.wav
2022-08-27 17:13:04,561 INFO    local           Got information about a file at /home/den/samples//BuzzBuzz_edited.wav
2022-08-27 17:13:04,561 INFO    local           Got information about a file at /home/den/samples//edited/Wow_Edited.wav
2022-08-27 17:13:04,561 INFO    local           Creating folder at /mnt/c/file_backup/samples
2022-08-27 17:13:04,566 INFO    local           Got information about a folder at /mnt/c/file_backup/samples
2022-08-27 17:13:04,567 INFO    local           Сopying File at /home/den/samples//SX_Door_origin.wav
2022-08-27 17:13:04,569 INFO    local           File at /home/den/samples//SX_Door_origin.wav is read
2022-08-27 17:13:04,571 INFO    local           Created new file at /mnt/c/file_backup/samples/SX_Door_origin.wav
2022-08-27 17:13:04,572 INFO    local           Сopying Folder at /home/den/samples//edited
2022-08-27 17:13:04,572 INFO    local           Creating folder at /mnt/c/file_backup/samples/edited
2022-08-27 17:13:04,579 INFO    local           Got information about a folder at /mnt/c/file_backup/samples/edited
2022-08-27 17:13:04,580 INFO    local           Сopying File at /home/den/samples//edited/Wow_Edited.wav
2022-08-27 17:13:04,581 INFO    local           File at /home/den/samples//edited/Wow_Edited.wav is read
2022-08-27 17:13:04,584 INFO    local           Created new file at /mnt/c/file_backup/samples/edited/Wow_Edited.wav
2022-08-27 17:13:04,586 INFO    local           Сopying File at /home/den/samples//SX_Phone_origin.wav
2022-08-27 17:13:04,588 INFO    local           File at /home/den/samples//SX_Phone_origin.wav is read
2022-08-27 17:13:04,590 INFO    local           Created new file at /mnt/c/file_backup/samples/SX_Phone_origin.wav
2022-08-27 17:13:04,591 INFO    local           Сopying File at /home/den/samples//BuzzBuzz_edited.wav
2022-08-27 17:13:04,594 INFO    local           File at /home/den/samples//BuzzBuzz_edited.wav is read
2022-08-27 17:13:04,596 INFO    local           Created new file at /mnt/c/file_backup/samples/BuzzBuzz_edited.wav
2022-08-27 17:13:04,598 INFO    app             Done in 0:00:00!
```
***

### SFTP Handler
We can specify `sftp` both as the input or output handlers using `-ih` and `-oh`:

> To use SFTP it is required to configre the following constants in the `config.py` file:  `HOST`,  `USERNAME`,  `KEY LOCATION`.

To upload the previous local `samples/` folder to the SFTP server, we should use the following command:
```sh
python main.py -i ~/samples/ -o /backups/samples -oh sftp
```
Program logging:
```sh
2022-08-27 17:34:14,438 INFO    app             Backuping files from /home/den/samples/ using local handler to backups/samples using local handler not using validators
2022-08-27 17:34:14,439 INFO    local           Got information about a folder at /home/den/samples/
2022-08-27 17:34:14,439 INFO    local           Got information about a file at /home/den/samples//SX_Door_origin.wav
2022-08-27 17:34:14,439 INFO    local           Got information about a folder at /home/den/samples//edited
2022-08-27 17:34:14,439 INFO    local           Got information about a file at /home/den/samples//SX_Phone_origin.wav
2022-08-27 17:34:14,439 INFO    local           Got information about a file at /home/den/samples//BuzzBuzz_edited.wav
2022-08-27 17:34:14,439 INFO    local           Got information about a file at /home/den/samples//edited/Wow_Edited.wav
2022-08-27 17:34:14,440 INFO    sftp            Creating folder at backups/samples
2022-08-27 17:34:14,771 INFO    sftp            Got information about a folder at backups/samples
2022-08-27 17:34:14,771 INFO    sftp            Сopying File at /home/den/samples//SX_Door_origin.wav
2022-08-27 17:34:14,790 INFO    local           File at /home/den/samples//SX_Door_origin.wav is read
2022-08-27 17:34:14,901 INFO    sftp            Created new file at backups/samples/SX_Door_origin.wav
2022-08-27 17:34:14,901 INFO    sftp            Сopying Folder at /home/den/samples//edited
2022-08-27 17:34:14,901 INFO    sftp            Creating folder at backups/samples/edited
2022-08-27 17:34:15,036 INFO    sftp            Got information about a folder at backups/samples/edited
2022-08-27 17:34:15,037 INFO    sftp            Сopying File at /home/den/samples//edited/Wow_Edited.wav
2022-08-27 17:34:15,055 INFO    local           File at /home/den/samples//edited/Wow_Edited.wav is read
2022-08-27 17:34:15,176 INFO    sftp            Created new file at backups/samples/edited/Wow_Edited.wav
2022-08-27 17:34:15,177 INFO    sftp            Сopying File at /home/den/samples//SX_Phone_origin.wav
2022-08-27 17:34:15,197 INFO    local           File at /home/den/samples//SX_Phone_origin.wav is read
2022-08-27 17:34:15,259 INFO    sftp            Created new file at backups/samples/SX_Phone_origin.wav
2022-08-27 17:34:15,259 INFO    sftp            Сopying File at /home/den/samples//BuzzBuzz_edited.wav
2022-08-27 17:34:15,279 INFO    local           File at /home/den/samples//BuzzBuzz_edited.wav is read
2022-08-27 17:34:15,459 INFO    sftp            Created new file at backups/samples/BuzzBuzz_edited.wav
2022-08-27 17:34:15,460 INFO    app             Done in 0:00:01!
```

The remote server has the following file structure:
```sh
root@vaua0073687:~/backups# tree ~/backups/
/root/backups/
└── samples
    ├── BuzzBuzz_edited.wav
    ├── edited
    │   └── Wow_Edited.wav
    ├── SX_Door_origin.wav
    └── SX_Phone_origin.wav

2 directories, 4 files
```

We can also swap the handlers:
```sh
python main.py -o ~/samples/ -i backups/samples -ih sftp -oh local
```

> If `-ih` or `-oh` keys are not specified, the `local` handler will be used
***

### Google Drive Handler

We can use Google Drive Handler to upload or download folders.

>To use GDrive handler, we should provide `secrets.json` file.

To upload `samples/` folder we will can use the following command:

```sh
python main.py -i ~/samples/ -o backups/samples -oh gdrive
```

Program output:
```sh
2022-08-27 17:43:17,764 INFO    app             Backuping files from /home/den/samples/ using local handler to backups/samples using local handler not using validators
2022-08-27 17:43:17,764 INFO    local           Got information about a folder at /home/den/samples/
2022-08-27 17:43:17,764 INFO    local           Got information about a file at /home/den/samples//SX_Door_origin.wav
2022-08-27 17:43:17,765 INFO    local           Got information about a folder at /home/den/samples//edited
2022-08-27 17:43:17,765 INFO    local           Got information about a file at /home/den/samples//SX_Phone_origin.wav
2022-08-27 17:43:17,765 INFO    local           Got information about a file at /home/den/samples//BuzzBuzz_edited.wav
2022-08-27 17:43:17,765 INFO    local           Got information about a file at /home/den/samples//edited/Wow_Edited.wav
2022-08-27 17:43:17,765 INFO    gdrive          Creating folder at backups/samples
2022-08-27 17:43:18,461 INFO    gdrive          Found records with name backups in folder 0AH3CXGph3HmOUk9PVA: 0
2022-08-27 17:43:19,363 INFO    gdrive          Created folder backups at
2022-08-27 17:43:19,640 INFO    gdrive          Found records with name samples in folder 1N9LMu8J4rQrLNwTYWcWh67FAF6a4Y3gs: 0
2022-08-27 17:43:20,254 INFO    gdrive          Created folder samples at /backups
2022-08-27 17:43:20,254 INFO    gdrive          Сopying File at /home/den/samples//SX_Door_origin.wav
2022-08-27 17:43:20,595 INFO    gdrive          Found records with name SX_Door_origin.wav in folder 1SgfUNnq8JVNNvJL5c1c9rMseiZ0oVpd2: 0
2022-08-27 17:43:20,595 INFO    local           File at /home/den/samples//SX_Door_origin.wav is read
2022-08-27 17:43:21,692 INFO    gdrive          Сopying Folder at /home/den/samples//edited
2022-08-27 17:43:21,692 INFO    gdrive          Creating folder at backups/samples/edited
2022-08-27 17:43:22,304 INFO    gdrive          Found records with name backups in folder 0AH3CXGph3HmOUk9PVA: 1
2022-08-27 17:43:22,304 INFO    gdrive          Folder backups is already exists at
2022-08-27 17:43:22,569 INFO    gdrive          Found records with name samples in folder 1N9LMu8J4rQrLNwTYWcWh67FAF6a4Y3gs: 1
2022-08-27 17:43:22,569 INFO    gdrive          Folder samples is already exists at /backups
2022-08-27 17:43:22,839 INFO    gdrive          Found records with name edited in folder 1SgfUNnq8JVNNvJL5c1c9rMseiZ0oVpd2: 0
2022-08-27 17:43:23,370 INFO    gdrive          Created folder edited at /backups/samples
2022-08-27 17:43:23,370 INFO    gdrive          Сopying File at /home/den/samples//edited/Wow_Edited.wav
2022-08-27 17:43:23,628 INFO    gdrive          Found records with name Wow_Edited.wav in folder 174fISaVT9lqcSKnHXLMTEoaTHifMiBXt: 0
2022-08-27 17:43:23,629 INFO    local           File at /home/den/samples//edited/Wow_Edited.wav is read
2022-08-27 17:43:24,820 INFO    gdrive          Сopying File at /home/den/samples//SX_Phone_origin.wav
2022-08-27 17:43:25,085 INFO    gdrive          Found records with name SX_Phone_origin.wav in folder 1SgfUNnq8JVNNvJL5c1c9rMseiZ0oVpd2: 0
2022-08-27 17:43:25,086 INFO    local           File at /home/den/samples//SX_Phone_origin.wav is read
2022-08-27 17:43:26,264 INFO    gdrive          Сopying File at /home/den/samples//BuzzBuzz_edited.wav
2022-08-27 17:43:26,498 INFO    gdrive          Found records with name BuzzBuzz_edited.wav in folder 1SgfUNnq8JVNNvJL5c1c9rMseiZ0oVpd2: 0
2022-08-27 17:43:26,498 INFO    local           File at /home/den/samples//BuzzBuzz_edited.wav is read
2022-08-27 17:43:27,634 INFO    app             Done in 0:00:10!
```

Google Drive folder contens:
![google drive folder](https://i.ibb.co/RSj33QV/image.png)

### Validators
If we try to copy the contents of the source folder:
```sh
python main.py -o /mnt/c/file_backup/source_code
```

We will see that the folder has ~14k files:
```sh
tree /mnt/c/file_backup/source_code/ | wc -l
14037
```

>If `-i` key is not specified, it will copy the current folder.

We can filter out unnecessary files (`.pyc` binaries, `.env` files, etc) by setting file\folder filtering using `config.py` fle using regular expressions:

```py
    EXCLUDED_NAMES = [
        r"^__",
        r"^env",
        r"^venv",
        r"^\.",
        "^lib$",
    ]
    EXCLUDED_FORMATS = [
        "pyc",
        "pyd",
    ]
```

To use them, we simply provide `-v` key:
```sh
python main.py -o /mnt/c/file_backup/source_code -v
```

Now the output folder conatins only 22 files:
```sh
tree /mnt/c/file_backup/source_code/ | wc -l
22
```
***
