import argparse
import happy_pony_synth

def main():
    print(happy_pony_synth.__file__)
    print(dir(happy_pony_synth))
    parser = argparse.ArgumentParser(description='Description of your script')
    parser.add_argument('midifilename', type=str, default="", help='Input midi file.')
    parser.add_argument('lilypondfilename', type=str, default="", help='Input lilypond file.')

    args = parser.parse_args()

    # Access the arguments
    print(f'Arguments: {args}')
    
    midifilename = args.midifilename
    lilypond_filename = args.lilypondfilename
    happy_pony_synth.convert_midi_to_wav( midifilename, lilypond_filename )
    
    print("Hello, World!")

if __name__ == "__main__":
    main()
