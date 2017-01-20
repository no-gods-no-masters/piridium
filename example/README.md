# Piridium Example Application
This example application demonstrates how to send and receive messages using the library.

A callback function is available for processing returned data -- this allows for complete flexibility regarding how you use the system to perform tasks or display results. Our first real-world project using Piridium involves triggering an alarm based on a signal sent from a server. The alarm signal is then distributed to RockBLOCKs with specific IMEIs.

We have included a stripped down version of that application as an example for others to work from.

## Dependencies
- [Piridium](https://github.com/no-gods-no-masters/piridium/)
- `./mt_receive.py`, `./mt_respond.py`, `./mo_send.py`
  - Raspbian (untested with other \*nix flavors)
- `./mt_send.py`
  - Raspbian, macOS, Ubuntu (untested with other \*nix flavors)

## Configuration
- Copy `./config-example.ini` to `./config.ini`
- Edit `./config.ini` and add your RockBLOCK authentication.
  - All instances of `config.ini` are addressed by `.gitignore`.
  - Never include authentication information in a Github repository!

### config.ini
#### imei
`identifier` (str) [ `000000000000000` ] A RockBLOCK identifier followed by the IMEI value for that RockBLOCK.

#### log
`log_name` (str) [ `app` ] Name of internal log.

`log_filename` (str) [ `app.log` ] Name of file log is saved to.

#### modem
`baud` (int) [`19200`] Baud rate to communicate with the port.

`port` (str) [`/dev/ttyUSB0`] Port to communicate with.

#### post
`url` (str) [ `https://core.rock7.com/rockblock/MT` ] Rock7 communication endpoint. This shouldn't change.

`username` (str) [ `username@domain.com` ] Your Rock7 username.

`password` (str) [ `password` ] Your Rock7 password.

#### respond
`match` (str) [ `"String to match"` ] String `mt_respond.py` looks for in incoming SBD messages.

`response` (str) [ `"Response to send"` ] String `mt_respond.py` responds with when messages contain `match` string.

## Receive & Process MT Data
`./mt_receive.py`

Run on the RockBLOCK and sets up a listener to await incoming and Mobile Terminated (MT) data and implements a callback function for processing the included messages. It needs to be running for messages from `mt_send.py` to be picked up.

## Respond to MT Data
`./mt_respond.py`

Run on the RockBLOCK, this script monitors the serial port and waits for incoming SBD messages. When one is received, it checks for a string as defined in `config.ini` . If the string matches, a reply (also defined in config.ini) is sent, else it just logs the incoming message.

## Send MT Data
`./mt_send.py`

This script lives on a server and allows data to be sent to a RockBLOCK specified by an IMEI via Mobile Terminated (MT) Short Burst Data (SBD) messages.

### Syntax
`./mt_send.py [options] "<message>"`

### Options
`-x` (str) [''] Read the config file for a user defined string representing the RockBLOCK's IMEI.

`-v` (bool) [off] Turn on verbose output messages.

`-t` (bool) [off] Test the send function but don't send the message. Turns on verbose output.

### Examples
`./mt_send.py -x abc "Hey, Mike!"`

Send `"Hey, Mike!"` to the RockBLOCK with the IMEI alias `abc` without verbose debug output.

`./mt_send.py -v -x def "Hey, Katéri!"`

Send `"Hey, Katéri!"` to the RockBLOCK with the IMEI alias `def` with verbose debug output.

`./mt_send.py -t -x hij "Hey, Greg!"`

Test send `"Hey, Greg!"` to the RockBLOCK with the IMEI alias `hij` with verbose debug output.

## Send MO Data
`./mo_send.py`

Allows MO (Mobile Originated) SBD (Short Burst Data) messages to be sent from a RockBLOCK to the RockBLOCK portal and then forwarded as necessary.  `mo_send.py` uses a queuing system based on writing outgoing messages to disk, and then sending from oldest to newest. If a message fails to send, it will be re-sent after a 45 second delay. This method avoids the need for a database, and allows for message persistence in the event of power loss.

### Syntax
`./mo_send.py [options] "<message>"`

### Examples
`./mo_send.py -v "ocean temp 17C"`

Sends the message `"ocean temp 17C"` as a MO (mobile originated) SBD message from the RockBLOCK to the RockBLOCK portal.
