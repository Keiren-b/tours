from tours.dataset import load_clean_data, cutoff_series, split_data


def main():
    df = load_clean_data()
    df = cutoff_series(df)
    train_df, val_df, test_df = split_data(df)


if __name__ == "__main__":
    main()