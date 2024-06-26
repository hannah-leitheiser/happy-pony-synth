import argparse
def main():
    parser = argparse.ArgumentParser(description='Description of your script')
    parser.add_argument('input-filename', type=str, default="", help='Input midi file.')

    args = parser.parse_args()

    # Access the arguments
    print(f'Arguments: {args}')
    
    print("Hello, World!")

if __name__ == "__main__":
    main()
