from tours.dataset import load_clean_data, cutoff_series


def main():
    df = load_clean_data()
    df = cutoff_series(df)
    print(df.shape)
    print(df.index.min(), df.index.max())


if __name__ == "__main__":
    main()