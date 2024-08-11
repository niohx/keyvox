import json
from keyvox import Keyvox
import datetime
def main():
    instance = Keyvox("Bw0yFwIVWFNRiZapLIgDyFdyIUsI10NvAZNqI3jP", "3Nr5EU4JhOTzOTMc1r2PI83lg6E0ZTfS1yX7ynQbeGdcMC6a")
    # units = instance.getUnits()
    pin = instance.getLockPinList("QRVPXSN8LDDW8COV",datetime.datetime(2024, 8, 8),datetime.datetime(2024, 8, 10))
    print(json.dumps(pin, indent=2))

if __name__ == "__main__":
    main()