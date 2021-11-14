# GnuVolca

Korg Volca Sample uploader for linux.

- [GnuVolca](#gnuvolca)
  - [Usage](#usage)
  - [Installation](#installation)
    - [Via virtualenv](#via-virtualenv)

## Usage
Store all the samples you want to upload on an empty directory.

Connect the audio out of your machine to the audio in on the Volca Sample at high volume. Make sure no other application which might produce sound is running. 

Pass the full path to the directory as an argument to gnuvolca.

**WARNING**: Do not execute the script without pluging the line out to your volca. Reproducing the raw audio through your speakers might damage them.

```bash
$ ./gnuvolca.py --dir /path/to/sample/pack
```

## Installation
### Via virtualenv
```bash
$ git clone https://github.com/grafuls/gnuvolca.git && cd gnuvolca
$ virtualenv .env && source .env/bin/activate
(.env)$ pip install -r requirements.txt
(.env)$ ./gnuvolca.py --dir /path/to/sample/pack
```