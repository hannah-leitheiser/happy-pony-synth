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

def voiceFunction(word, volume,sampleRate=48000):
    print(word )
    if "[" in word and "]" in word:
        word = (word.split("[")[1]).split("]")[0]
    os.system("pico2wave --wave=t.wav \"" + word + "\"")
    samplerate, data = wavfile.read('t.wav')
    #wordIndex = wordIndex + 1
    outWave = []
    for x in data:
        outWave.append(x * (volume/127))
        outWave.append(x * (volume/127))
        outWave.append(x * (volume/127))
    return outWave

class Program:
    def __init__( self, name, adsr, fm_overtone_modulation_proportion_matrix ):
        self.name = name
        self.adsr = adsr
        self.fm_overtone_modulation_proportion_matrix = fm_overtone_modulation_proportion_matrix

    def synthesize_fm_wave( self, note, duration, volume, sampleRate=48000):
        pass

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


class FMModulationMatrix:
    def __init__(self, absolute_frequency_matrix, overtone_matrix):
        self.overtone_matrix = overtone_matrix
        self.absolute_frequency_matrix = absolute_frequency_matrix


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


def generate_modulator_signal(note, duration, FM_matrix, sample_rate):
    note_frequency = note.get_frequency_in_Hz()
    note_period_samples = sample_rate / note_frequency
    signal = []
    for x in range(int(duration*sample_rate)):
        sample = 0
        for overtone in range(len(FM_matrix.overtone_matrix)):
            theta_fundamental = math.pi * 2 * (x / note_period_samples)
            theta = theta_fundamental * FM_matrix.overtone_matrix[overtone][0]
            amount = note_frequency * FM_matrix.overtone_matrix[overtone][1]
            sample += math.sin(theta) * amount
        for f in range(len(FM_matrix.absolute_frequency_matrix)):
            frequency = FM_matrix.absolute_frequency_matrix[f]
            theta = math.pi * 2 * (frequency[0] / sample_rate)
            amount = frequency[1] * note_frequency
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



def soundFunction(note, duration, volume, program, sampleRate=48000):
    if volume <= 0:
          return []
    noteSample=[]
    n = MusicalNote(note, volume, duration)
    a = program.adsr
    a_curve = generate_asdr_envelope(n, a, sampleRate)
    m = program.fm_overtone_modulation_proportion_matrix
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


def convert_midi_to_wav( midifilename, lilypond_filename ):
    programs = dict()
    for line in open(lilypond_filename).readlines():
        if "Program " in line:
            a = line
            a=a.replace(" ","")
            a=a.replace("\"", "")
            a=a.replace("\n","")
            a=a.split("Program")[1]
            program = int(a.split(":")[0])
            adsr = a.split(":")[1]
            adsr = adsr.replace("s","")
            adsr = adsr.replace("%","")
            adsr = adsr.split(",")
            
            a=a.split(":")[2]
            a=a.replace(",","")
            a=a.split("][")
            
            programs[program] = {"absolute":[], "relative":[], "adsr" : (float(adsr[0]), float(adsr[1]), float(adsr[2])/100, float(adsr[3]))}
            for x in a:
                x = x.replace("[","")
                x = x.replace("]","")
                if "Hz" in x:
                    hz = float(x.split("Hz")[0])
                    amount = float(x.split("Hz")[1][:-1])
                    programs[program]["absolute"].append((hz, amount/100))
                if "x" in x:
                    xx = float(x.split("x")[0])
                    amount = float(x.split("x")[1][:-1])
                    programs[program]["relative"].append((xx, amount/100))
    print(programs)
    
    midi_data = read_midi_file.produce_midi_arrays( midifilename )
    outputfilename = os.path.splitext(midifilename)[0]
    
    sample_rate = 48000
    afile = aifc.open(outputfilename+".aiff", "wb")
    afile.aiff()
    afile.setnchannels(1)
    afile.setsampwidth(2)
    afile.setframerate(sample_rate)

    sound = [0]*(int(sample_rate*(midi_data["length"]+1)))


    # notes (time_start, duration, note_number, velocity, program, channel, track )
    for note in midi_data["notes"]:
       print(note)
       #class ADSR:
       #__init__(attack_time, decay_time,  
       #        sustain_level, release_time):
       modulation = Program("None", ADSR(0.5,0.8, 0.5, 0.5), FMModulationMatrix( [], [] ))
       if int(note[4]) in programs.keys():
           adsr = programs[int(note[4])]["adsr"]
           modulation = Program(note[4], ADSR(adsr[0], adsr[1], adsr[2], adsr[3]),FMModulationMatrix( programs[int(note[4])]["absolute"], programs[int(note[4])]["relative"] ))
        
       noteSamples = soundFunction( note[2], note[1], note[3], modulation, sample_rate)
       for x in range(len(noteSamples)):
          if int(x + note[0]*sample_rate) < len(sound):
             sound[ int(note[0]*sample_rate + x) ] = sound[ int(note[0]*sample_rate + x) ] + noteSamples[x]

    # lyrics ( time_start, text, track )
    bias = -0.1
    for word in midi_data["lyrics"]:
       print(word)
       noteSamples = voiceFunction( word[1], 20)
       for x in range(len(noteSamples)):
          if int(x + word[0]*sample_rate + bias*sample_rate) < len(sound) and int(x + word[0]*sample_rate + bias*sample_rate) >= 0:
             sound[ int(word[0]*sample_rate + x + sample_rate*bias) ] = sound[ int(word[0]*sample_rate + x + sample_rate*bias) ] + noteSamples[x]


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
