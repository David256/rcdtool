# rcdtool

Script that downloads telegram restricted content.

## Usage

For help:

```bash
./rcdtool --help
```

Normally, the script will take the channel and message IDs from the CLI argument, but if you did not provide them, then the script will prompt your for each missing ID. You can also customize the output filename.

If you have channel and message IDs you can do:
```bash
./rcdtool -c /path/to/config.ini -C <channel ID here> -M <message ID here> -O interesting-video.mp4
```
Then the script starts the downloading.

Well, if you use the Python script, then change `rcdtool` by `python rcdtool` et voilà.

### Where I find these IDs?

In desktop: right click > copy message/post link.
In mobile: touch the message > copy link

This link will have this format:
```
https://t.me/c/<channel ID>/<message ID>
```

Then, extract the IDs from the link. Or you can pass that link to the tool with `--link` as follows:
```bash
./rcdtool --link https://t.me/c/106942033f/123 -O stuff.png
```

## Dist

In this repository we release the source code (Python) and a binary option for GNU/Linux. You can build a binary for any other operating system using tool as [PyInstaller](https://pyinstaller.org/en/).

## Telegram session

You MUST have an API ID provided by Telegram at https://my.telegram.org/ (I think). This is as follows:
```
api_id: 32767
api_hash: ed855a59bbe4a3360dbf7a0538842142
```
Then rename `config.ini.sample` to `config.ini`, edit it and save wherever you want. If the file is in the same directory as `rcdtool` and its name is exactly "config.ini", then `rcdtool` will load it automatically.

The first time, **rcdtool** will ask you for your phone number, and will start a login process. When this is done, a `.session` file will be created. With this `.session` file, the tool could access to your Telegram account to read messages and download medias. The name of the .session file is set in `config.ini`.
