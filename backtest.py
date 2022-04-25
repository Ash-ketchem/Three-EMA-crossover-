"""
Function to backtest the trades.
This function decides if a trade is a win, loss or even. 

"""
def backtest(df, df_len, trades, tp, sl, profits, losers, even=True):
    max_winner_in_a_row = max_losers_in_a_row = losers_count = winners_count = 0

    if even: evens = []

    for trade in trades:
        bar_index = trade.get("bar_index")
        value = trade.get("entry_price")
        trade_type = trade.get("type")

        if trade_type == "long":
            take_profit = value * (1 + tp / 100)
            stop_loss = value * (1 - sl / 100)
            break_even = value * (1 + sl / 100)

        if trade_type == "short":
            take_profit = value * (1 - tp / 100)
            stop_loss = value * (1 + sl / 100)
            break_even = value * (1 - sl / 100)

        new_sl = sl

        for i in range(bar_index, df_len):

            if trade_type == "long":
                if df["Close"][i] >= break_even:
                    stop_loss = break_even
                    new_sl = 0

            if trade_type == "short":
                if df["Close"][i] <= break_even:
                    stop_loss = break_even
                    new_sl = 0
                    
            data = {
                "type" : trade.get("type"),
                "bar_index" : trade.get("bar_index"),
                "entry_price" : trade.get("entry_price"),
                "closing_index": i,
                "closing_price_close" : df["Close"][i],
                "closing_price_open" : df["Open"][i],
                "closing_price_High" : df["High"][i],
                "closing_price_Low" : df["Low"][i],
                "stop loss %" : new_sl,
                "take profit %": tp,
                "stop loss" : stop_loss,
                "take profit" : take_profit,
                "break_even" : break_even
                }

            # trade["closing_price_close"] = df["Close"][i]

            if trade_type == "long":

                if df["Close"][i] >= take_profit:
                    profits.append(data)
                    losers_count = 0
                    winners_count += 1
                    max_winner_in_a_row = max(max_winner_in_a_row, winners_count)
                    break

                elif df["Close"][i] <= stop_loss:
                    if even:
                        if data.get("stop loss %") == 0:
                            evens.append(data)
                            losers_count = 0
                            winners_count += 1
                            max_winner_in_a_row = max(max_winner_in_a_row, winners_count)
                        else:
                            losers.append(data)
                            winners_count = 0
                            losers_count += 1
                            max_losers_in_a_row = max(max_losers_in_a_row, losers_count)

                    break

            if trade_type == "short":

                if df["Close"][i] <= take_profit:
                    profits.append(data)
                    losers_count = 0
                    winners_count += 1
                    max_winner_in_a_row = max(max_winner_in_a_row, winners_count)
                    break

                elif df["Close"][i] >= stop_loss:
                    if even:
                        if data.get("stop loss %") == 0:
                            evens.append(data)
                            losers_count = 0
                            winners_count += 1
                            max_winner_in_a_row = max(max_winner_in_a_row, winners_count)
                        else:
                            losers.append(data)
                            winners_count = 0
                            losers_count += 1
                            max_losers_in_a_row = max(max_losers_in_a_row, losers_count)

                    break

    return (max_losers_in_a_row, max_losers_in_a_row, evens) if even else (max_losers_in_a_row, max_losers_in_a_row)
