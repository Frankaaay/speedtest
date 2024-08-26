var = "ping192"
var2 = "jitter"

def summarize(df):
    mean = df[var].mean()
    max = df[var].max()
    low = df[var].low()
    std_age = df[var].std()
    word_count = df['ping192'].str.contains(r'\b{}\b'.format("inf"), case=False).sum()

    return mean, max, low, std_age, word_count
