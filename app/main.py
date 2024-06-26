import argparse
def main():
    parser = argparse.ArgumentParser(description='Description of your script')
    parser.add_argument('--optional_arg', type=int, default=0, help='Description of an optional argument')

    args = parser.parse_args()

    # Access the arguments
    print(f'Optional Argument: {args.optional_arg}')
    
    print("Hello, World!")

if __name__ == "__main__":
    main()
