import json
from keyvox import Keyvox

def main():
    instance = Keyvox("Bw0yFwIVWFNRiZapLIgDyFdyIUsI10NvAZNqI3jP", "3Nr5EU4JhOTzOTMc1r2PI83lg6E0ZTfS1yX7ynQbeGdcMC6a")
    units = instance.getUnits()
    print(json.dumps(units, indent=2))

if __name__ == "__main__":
    main()