import argparse


def main():
    parser = argparse.ArgumentParser(description='Interactive Log Viewer')
    parser.add_argument('--help', action='help', help='Display this help menu')
    parser.add_argument('--view', choices=['date', 'level', 'keyword'], help='View logs by date range, log level, or keyword')
    args = parser.parse_args()

    if args.view:
        print(f'Viewing logs by: {args.view}')
    else:
        print('Please select a viewing option using --view.')


if __name__ == '__main__':
    main()