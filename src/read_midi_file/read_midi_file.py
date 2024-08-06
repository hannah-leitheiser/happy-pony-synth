import mido

def get_ticks_per_second(midi_file_path):
    midi_file = mido.MidiFile(midi_file_path)
    ticks_per_beat = midi_file.ticks_per_beat

    for msg in midi_file:
        if msg.type == 'set_tempo':
            microseconds_per_quarter_note = msg.tempo
            ticks_per_second = ticks_per_beat / (microseconds_per_quarter_note / 1000000)
            return ticks_per_second

    return None  # Return None if no tempo information found


def produce_midi_arrays(midi_file_path):
    notes = list()
    lyrics = list()
    midi_file = mido.MidiFile(midi_file_path)
    ticks_per_second = get_ticks_per_second(midi_file_path)
    track_is_vocal = False
    vocal_notes = dict()
    for t in range(len(midi_file.tracks)):
        channels = dict()
        track = midi_file.tracks[t]
        current_tick = 0
        for msg in track:
            print((msg, t))
            current_tick+=msg.time
            #  Message('program_change', channel=3, program=9, time=0)
            if msg.type == "program_change":
                channels[msg.channel] = msg.program
            #  MetaMessage('track_name', name='singer:vocal', time=0)
            if msg.type == "track_name":
                if msg.name = "singer:vocal":
                    track_is_vocal = True
            if msg.type == "lyrics":
                # lyrics ( time_start, text, track )
                lyrics.append( (current_tick/ticks_per_second, msg.text, t))
            if msg.type == "note_on":
                if hasattr(msg, 'velocity') and msg.velocity > 0:
                    program = -1
                    if msg.channel in channels:
                        program = channels[msg.channel]
                    current_notes[msg.note] = (msg.velocity, current_tick, program)
                if hasattr(msg, 'velocity') and msg.velocity == 0:
                    note_to_save = current_notes.pop(msg.note)
                    # notes (time_start, duration, note_number, velocity, program, channel, track )
                    if track_is_vocal:
                        print("vocal")
                    else:
                        notes.append ( (note_to_save[1]/ticks_per_second, 
                                    (current_tick - note_to_save[1]) / ticks_per_second, 
                                    msg.note, note_to_save[0], note_to_save[2], msg.channel, t))

    return {"notes":notes, "lyrics": lyrics, "length" : midi_file.length }
