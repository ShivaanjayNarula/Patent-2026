from coral_restoration.simulation import run_simulation


if __name__ == "__main__":
    log = run_simulation(ticks=30, tick_ms=250)
    print("Summary:", log.summary())
