# GnuVolca

Korg Volca Sample uploader for linux.

- [GnuVolca](#gnuvolca)
  - [Usage](#usage)
  - [Installation](#installation)
    - [Via virtualenv](#via-virtualenv)

<br>

## Usage
Place the samples you want to upload in an empty directory.

Connect the audio out of your machine to the audio in on the Volca Sample at high volume. Make sure no other application which might produce sound is running. 

Pass the full path to the directory as an argument to gnuvolca.

**WARNING**: Do not execute the script without pluging the line out to your volca. Reproducing the raw audio through your speakers might damage them.

```bash
$ ./gnuvolca.py --dir /path/to/sample/pack
```

<br>

## Sample Requirements

<br>

### File Size
The Korg Volca Sample has a memory of 2 MB, so the total size of all samples
cannot exceed this hardware limit. See ```Preprocessing``` for how to change
the sample rate to reduce the individual file sizes.

<br>

## File Encoding
The Korg Volca Sample supports 16-bit depth signed-integer encoding for the 
wav files. See ```Preprocessing``` for how to change the file encoding.

<br>

## Preprocessing
To both ensure correct encoding, and change the samplerate of the samples to
4000 Hz, run the following shell script from the directory containing the samples (requires sox):

```bash
for file in *.wav; do 
  sox "$file" -e signed-integer -b 16 "resampled/${file%.wav}_resampled.wav" rate 4000; 
done
```

<br>

## Installation
### Via virtualenv
```bash
$ git clone https://github.com/grafuls/gnuvolca.git && cd gnuvolca
$ python3.10 -m venv .env && source .env/bin/activate
(.env)$ pip install -r requirements.txt
```

## Loading Samples
```bash
$ source .env/bin/activate
(.env)$ ./gnuvolca.py --dir /path/to/sample/pack
```

## Clearing all Samples
```bash
$ source .env/bin/activate
(.env)$ ./gnuvolca.py -c
```
