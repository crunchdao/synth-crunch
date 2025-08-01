import sys


def check_installed():
    try:
        import synth
    except ImportError:
        print("`synth_subnet` package is not installed.", file=sys.stderr)
        print("Please install it with: pip install synth-crunch[infra]", file=sys.stderr)

        exit(1)
