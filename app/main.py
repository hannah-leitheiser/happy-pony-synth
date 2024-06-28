import argparse
import synth

def main():
    parser = argparse.ArgumentParser(description='Description of your script')
    parser.add_argument('midifilename', type=str, default="", help='Input midi file.')

    args = parser.parse_args()

    # Access the arguments
    print(f'Arguments: {args}')
    
    midifilename = args.midifilename
    synth.convert_midi_to_wav( midifilename ):
    
    print("Hello, World!")

if __name__ == "__main__":
    main()
