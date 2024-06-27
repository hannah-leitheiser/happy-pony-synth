import argparse
import mido

def main():
    parser = argparse.ArgumentParser(description='Description of your script')
    parser.add_argument('midifilename', type=str, default="", help='Input midi file.')

    args = parser.parse_args()

    # Access the arguments
    print(f'Arguments: {args}')

    songname = args.midifilename
    mid = mido.MidiFile(songname)
    for msg in mid:
        print(msg)
    
    print("Hello, World!")

if __name__ == "__main__":
    main()
