import midi
import aifc
import struct
import random
import os


from scipy.io import wavfile

tick=60
SampleRate=48000
maxAmplitude = 0x7FFF
minAmplitude = -0x8000

wordsText = """

stay safe stay home
le tle po ne do not roam
stay home stay safe
kind ness to re main in place
stay safe stay home
be good at home 
it's nice at home

the world has got ten
dan ger us go on ly when you must
be care full who you talk to
be care full who you trust
"""

words = wordsText.replace("\n", " ")
while ( words.replace("  ", " ") != words):
    words = words.replace("  ", " ")
words = words.split(" ")
if words[0] == "":
    words = words[1:]
wordIndex = 0

def voiceFunction(note, duration, volume, voice=0,sampleRate=48000, tic=tick):
    global wordIndex
    if not (wordIndex < len(words)):
        print("Word index = " + str(wordIndex) + ", out of range.")
        return []
    print(words[wordIndex] )
    os.system("pico2wave --wave=t.wav \"" + words[wordIndex] + "\"")
    samplerate, data = wavfile.read('t.wav')
    wordIndex = wordIndex + 1
    outWave = []
    for x in data:
        outWave.append(x * (volume/127))
        outWave.append(x * (volume/127))
        outWave.append(x * (volume/127))
    return outWave



def soundFunction(note, duration, volume, voice=0,sampleRate=48000, tic=tick):
      if volume <= 0:
          return []
      noteSample=[]
      frequencyHz = 440*2**((note-69)/12);
      #print ( (note, duration, volume, frequencyHz))
      cycles = duration*tic // (sampleRate / frequencyHz)
      if frequencyHz < 100:
         amplitude= 0.3*(  (volume/127) * (maxAmplitude - minAmplitude) )
      else: 
         amplitude= 0.3*( 100 * (volume/127) * (maxAmplitude - minAmplitude) ) / frequencyHz
      x=0
      while(amplitude > 0.1):
         proportion = x - (x // (sampleRate / frequencyHz)) * (sampleRate / frequencyHz)
         proportion = proportion / (sampleRate / frequencyHz)
         if proportion < 0.25:
            triangle = proportion * 2
         else:
            if proportion < 0.75:
               triangle = 0.5 - (proportion - 0.25) * 2
            else:
               triangle = -0.5 + (proportion - 0.75) * 2
        
         #level=triangle * ( (amplitude*8000)/ frequencyHz**1)
         level = triangle * amplitude
         noteSample.append(level)
         if x > duration * tick:
            amplitude = ((amplitude ** 2) * 0.9995) ** 0.5
         x=x+1
      return noteSample


notes=[]
vocals=[]
reset = False
for track in midi.read_midifile("eastersong.mid"):
    ticklocation=0
    for line in str(track).split("\n"):
       print(line)
       if not reset and "channel=1" in line:
           reset = True
           ticklocation = 0
       if line[:20] == "   midi.NoteOnEvent(":
          if ' 0]' not in line:
             ticklocation = ticklocation + int( line[25:].split(",")[0])
             if "channel=0" in line:
                notes.append( (ticklocation, int(line[25:].split("[")[1].split(",")[0]) , int(line[25:].split("]")[0].split("data=[")[1].split(" ")[1]) ) )
             if "channel=1" in line:
                print("Vocal tick location: " + str(ticklocation))
                vocals.append( (ticklocation, int(line[25:].split("[")[1].split(",")[0]) , int(line[25:].split("]")[0].split("data=[")[1].split(" ")[1]) ) )

          else:
             ticklocation = ticklocation + int( line[25:].split(",")[0])
             thenote = 0

             
             if "channel=0" in line:
                 for aa in range(len(notes)):
                    if notes[aa][1] ==  int(line[25:].split("[")[1].split(",")[0]):
                       thenote=aa
                 notes[thenote] = (notes[thenote][0], notes[thenote][1], ticklocation, notes[thenote][2])

             if "channel=1" in line:
                 for aa in range(len(vocals)):
                    if vocals[aa][1] ==  int(line[25:].split("[")[1].split(",")[0]):
                       thenote=aa
                 vocals[thenote] = (vocals[thenote][0], vocals[thenote][1], ticklocation, vocals[thenote][2])

afile = aifc.open("test.aiff", "wb")
afile.aiff()
afile.setnchannels(1)
afile.setsampwidth(2)
afile.setframerate(48000)
import struct

sound = [0]*(48000*300)

import math



for note in notes:
   print(note)
   noteSamples = soundFunction( note[1], note[2]-note[0], note[3], 2)
   for x in range(len(noteSamples)):
      if x + note[0]*tick < len(sound):
         sound[ note[0]*tick + x ] = sound[ note[0]*tick + x ] + noteSamples[x]


for word in vocals:
   print(word)
   note = word
   noteSamples = voiceFunction( note[1], note[2]-note[0], note[3], 2)
   for x in range(len(noteSamples)):
      if x + note[0]*tick < len(sound):
         sound[ note[0]*tick + x ] = sound[ note[0]*tick + x ] + noteSamples[x]


for a in range(len(sound)):
   sound[a] = int(sound[a])
   #print(sound[a])
   if sound[a] > 0x7FFF:
      print("clipping")
      sound[a] = 0x7FFF;
   if sound[a] < -0x8000:
      print("clipping")
      sound[a] = -0x8000;


afile.writeframes( struct.pack('>'+'h'*len(sound), *sound))
afile.close()
