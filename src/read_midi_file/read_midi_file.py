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
    for t in range(len(midi_file.tracks)):
        track = midi_file.tracks[t]
        current_tick = 0
        current_notes = dict()
        for msg in track:
            current_tick+=msg.time
            if msg.type == "lyrics":
                lyrics.append( (current_tick, msg.text, msg.track))
            if msg.type == "note_on":
                if hasattr(msg, 'velocity') and msg.velocity > 0:
                    current_notes[msg.note] = (msg.velocity, current_tick)
                if hasattr(msg, 'velocity') and msg.velocity == 0:
                    note_to_save = current_notes.pop(msg.note)
                    notes.append ( (note_to_save[1], current_tick - note_to_save[1], msg.note, note_to_save[0], msg.track))

    return {"note":notes, "lyrics": lyrics)
