import math

import midi
import aifc
import struct
import random
import os
import math


from scipy.io import wavfile

import read_midi_file

tick=60
SampleRate=48000
maxAmplitude = 0x7FFF
minAmplitude = -0x8000

wordsText = """

"""

words = wordsText.replace("\n", " ")
while ( words.replace("  ", " ") != words):
    words = words.replace("  ", " ")
words = words.split(" ")
if words[0] == "":
    words = words[1:]
wordIndex = 0

def voiceFunction(note, duration, volume, tic, word, voice=0,sampleRate=48000):
    print(word )
    os.system("pico2wave --wave=t.wav \"" + word + "\"")
    samplerate, data = wavfile.read('t.wav')
    #wordIndex = wordIndex + 1
    outWave = []
    for x in data:
        outWave.append(x * (volume/127))
        outWave.append(x * (volume/127))
        outWave.append(x * (volume/127))
    return outWave

class Voice:
    def __init__( name, asdr, fm_overtone_modulation_proportion_matrix ):
        self.name = name
        self.asdr = asdr
        self.fm_overtone_modulation_proportion_matrix = fm_overtone_modulation_proportion_matrix

    def synthesize_fm_wave( self, note, duration, volume, sampleRate=48000):
        pass




def get_channel(line):
    if "channel=0" in line:
        return 0
    if "channel=1" in line:
        return 1
    if "channel=2" in line:
        return 2
    if "channel=3" in line:
        return 3




class ADSR:
    def __init__(self, attack_time, decay_time, 
            sustain_level, release_time):
        self.attack_time = attack_time
        self.decay_time = decay_time
        self.sustain_level = sustain_level
        self.release_time = release_time

class MusicalNote:
    def __init__(self, note, volume, duration):
        self.note = note # midi number
        self.volume = volume
        self.duration = duration

    def get_frequency_in_Hz(self):
        frequency_Hz = 440*2**((self.note-69)/12)
        return frequency_Hz


def scale_amplitude( note):
    if note.get_frequency_in_Hz() < 100:
         amplitude= 0.2*(  (note.volume/127) * (maxAmplitude - minAmplitude) )
    else: 
         amplitude= 0.2*( 100 * (note.volume/127) * (maxAmplitude - minAmplitude) ) / note.get_frequency_in_Hz()

    return amplitude 


class OvertoneFMModulationMatrix:
    def __init__(self, matrix):
        self.matrix = matrix


def generate_asdr_envelope(note, adsr, sample_rate):
    total_duration = note.duration + adsr.release_time # seconds
    samples = sample_rate * total_duration
    envelope = []
    # from zero to volume level at attack time
    note_phase = "attack"
    x = 0
    current_amplitude = 0
    peak_amplitude = scale_amplitude(note)
    while( x < samples ):
        envelope.append(current_amplitude)
        if note_phase == "attack":
            current_amplitude += peak_amplitude / (adsr.attack_time * sample_rate)
            if x > adsr.attack_time * sample_rate:
                note_phase = "decay"
        if note_phase == "decay":
            current_amplitude -= ((1-adsr.sustain_level) * peak_amplitude) / (adsr.decay_time * sample_rate)
            if x > (adsr.attack_time + adsr.decay_time) * sample_rate:
                note_phase = "sustain"
        x+=1
    note_phase = "release"
    while ( current_amplitude > 0.01 ):
        envelope.append(current_amplitude)
        current_amplitude -= ((adsr.sustain_level) * peak_amplitude) / (adsr.release_time * sample_rate)
        x+=1
    return envelope


def generate_modulator_signal(note, duration, overtone_matrix, sample_rate):
    note_frequency = note.get_frequency_in_Hz()
    note_period_samples = sample_rate / note_frequency
    signal = []
    for x in range(int(duration*sample_rate)):
        sample = 0
        for overtone in range(len(overtone_matrix.matrix)):
            theta_fundamental = math.pi * 2 * (x / note_period_samples)
            theta = theta_fundamental * (overtone + 2)
            amount = note_frequency * overtone_matrix.matrix[overtone]
            sample += math.sin(theta) * amount
        signal.append(sample)
    return signal


            
def am_modulate( signal, modulator):
    output = []
    for x in range(len(signal)):
        output.append( signal[x] * modulator[x] )
    return output


def fm_modulate( carrier_frequency, modulator, sample_rate ):
    output = []
    theta = 0
    minimum_frequency = 1
    for x in range(len(modulator)):
        modulated_frequency = carrier_frequency + modulator[x]
        modulated_frequency = max(modulated_frequency, minimum_frequency)
        modulated_samples_per_period = sample_rate/modulated_frequency
        modulated_added_theta = math.pi * 2 * (1 / modulated_samples_per_period)
        output.append ( math.sin( theta) )
        theta += modulated_added_theta
    return output



def soundFunction(note, duration, volume, voice=0,sampleRate=48000, tic=tick):
    if volume <= 0:
          return []
    noteSample=[]
    n = MusicalNote(note, volume, (duration*tick)/sampleRate)
    #class ADSR:
    #__init__(attack_time, decay_time,  
    #        sustain_level, release_time):
    a = ADSR( 0.1, 0.1, 0.7, 0.05)
    a_curve = generate_asdr_envelope(n, a, sampleRate)
    m = OvertoneFMModulationMatrix([1, 0.0, 0.0, 0.0, 0.0, 0.0])
    ms = generate_modulator_signal(n, len(a_curve)/sampleRate, m, sampleRate)
    fm = fm_modulate( n.get_frequency_in_Hz(), ms, sampleRate)
    noteSample = am_modulate( fm, a_curve)
    return noteSample
    r="""

 
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
      """


def convert_midi_to_wav( midifilename ):
    midi_data = read_midi_file.produce_midi_arrays( midifilename )
    outputfilename = os.path.splitext(midifilename)[0]
    notes=[]
    vocals=[]
    currentChannel = 0
    for track in midi.read_midifile(midifilename):
        ticklocation=0
        for line in str(track).split("\n"):
           print(line)
           if currentChannel != get_channel(line):
               currentChannel = get_channel(line)
               ticklocation = 0
           if line[:20] == "   midi.LyricsEvent(":
              #   midi.LyricsEvent(tick=384, text='1', data=[49]),
              if ' 0]' not in line:
                ticklocation = ticklocation + int( line[25:].split(",")[0])
              vocals.append( (ticklocation, line.split("text='")[1].split("', ")[0] ) )


           if line[:20] == "   midi.NoteOnEvent(":
              if ' 0]' not in line:
                 ticklocation = ticklocation + int( line[25:].split(",")[0])
                 if "channel=0" in line or True:
                   notes.append( (ticklocation, int(line[25:].split("[")[1].split(",")[0]) , int(line[25:].split("]")[0].split("data=[")[1].split(" ")[1]) ) )
                 #if "channel=1" in line:
                 #   print("Vocal tick location: " + str(ticklocation))
                 #   vocals.append( (ticklocation, int(line[25:].split("[")[1].split(",")[0]) , int(line[25:].split("]")[0].split("data=[")[1].split(" ")[1]) ) )

              else:
                 ticklocation = ticklocation + int( line[25:].split(",")[0])
                 thenote = 0

             
                 if "channel=0" in line or True:
                     for aa in range(len(notes)):
                        if notes[aa][1] ==  int(line[25:].split("[")[1].split(",")[0]):
                           thenote=aa
                     notes[thenote] = (notes[thenote][0], notes[thenote][1], ticklocation, notes[thenote][2])

                 #if "channel=1" in line:
                 #    for aa in range(len(vocals)):
                 #       if vocals[aa][1] ==  int(line[25:].split("[")[1].split(",")[0]):
                 #          thenote=aa
                 #    vocals[thenote] = (vocals[thenote][0], vocals[thenote][1], ticklocation, vocals[thenote][2])

    afile = aifc.open(outputfilename+".aiff", "wb")
    afile.aiff()
    afile.setnchannels(1)
    afile.setsampwidth(2)
    afile.setframerate(48000)

    sound = [0]*(48000*300)




    for note in notes:
       print(note)
       noteSamples = soundFunction( note[1], note[2]-note[0], note[3], 2)
       for x in range(len(noteSamples)):
          if x + note[0]*tick < len(sound):
             sound[ note[0]*tick + x ] = sound[ note[0]*tick + x ] + noteSamples[x]


    for word in vocals:
       print(word)
       note = word
       noteSamples = voiceFunction( 0, 0, 100, 2, note[1])
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
