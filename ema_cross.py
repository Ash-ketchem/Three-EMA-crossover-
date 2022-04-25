import yfinance as yf
import json

# import from files
from backtest import backtest
from params import paramaters as bp



# To calculate momemtum of close prices of a given time period
def calculate_momentum(closes, n):
    s = 0

    for i in range(1, len(closes)):
        s += closes[i] - closes[i-1]

    return s


class ThreeEma:

    def __init__(self, use_model=True,):
        self.asset = bp["asset"]
        self.time_frame = bp["time_frame"]
        self.time_period = bp["time_period"]
        self.tp = bp["tp"]
        self.sl = bp["sl"]
        self.emas = bp["ema_list"]
        self.period={
            "start": bp["training_period"]["start"].strftime("%Y-%m-%d"), "end": bp["training_period"]["end"].strftime("%Y-%m-%d")
        }

        self.df = yf.download(self.asset, period=self.time_period, interval=self.time_frame)

        self.df["Date"] = self.df.index.strftime("%d:%m:%y")

        # Algorithmatic conditions for trade entries

        self.short_crossover_med = False
        self.med_crossover_long = False

        self.short_crossunder_med = False
        self.med_crossunder_long = False

        self.profits, self.losses, self.break_evens = [], [], []
        self.trades = []
        self.long_profits, self.long_losses, self.short_profits, self.short_losses = [], [], [], []

        self.even = True
        self.full_win_trades = 0
        self.break_even_trades = 0
        self.max_winners_in_a_row = 0
        self.max_losers_in_a_row = 0
        self.max_trades_in_a_day = bp["max_trades"]


    def indicators(self):
        self.df[f"short_ema"] = self.df["Close"].ewm(span=self.emas[0]).mean()
        self.df[f"med_ema"] = self.df["Close"].ewm(span=self.emas[1]).mean()
        self.df[f"long_ema"] = self.df["Close"].ewm(span=self.emas[2]).mean()
        self.df["Momentum"] = self.df["Close"].diff(10)  # ten period Momentum of asset close prices

    def check_conditions(self, index):

        if self.df["short_ema"][index] > self.df["med_ema"][index] and self.df["short_ema"][index-1] <=  self.df["med_ema"][index-1]:
            self.short_crossover_med = True

        if self.df["med_ema"][index] > self.df["long_ema"][index] and self.df["med_ema"][index-1] <=  self.df["long_ema"][index-1]:
            self.med_crossover_long = True


        if self.df["short_ema"][index] < self.df["med_ema"][index] and self.df["short_ema"][index-1] >=  self.df["med_ema"][index-1]:
            self.short_crossunder_med = True


        if self.df["med_ema"][index] < self.df["long_ema"][index] and self.df["med_ema"][index-1] >=  self.df["long_ema"][index-1]:
            self.med_crossunder_long = True

  

    def strategy(self):

        for i in range(1, len(self.df)):

            self.check_conditions(i)

            if self.short_crossover_med:
                if self.med_crossover_long and self.df["Momentum"][i] > 0:
                    if True:
                        self.trades.append({
                            "type" : "long",
                            "bar_index": i if i == len(self.df) - 1 else i + 1,
                            "entry_price" : self.df["Open"][i] if i == len(self.df) - 1 else self.df["Open"][i+1]
                        })
                    self.short_crossover_med = self.med_crossover_long = False # Resetting generated trade conditions

            elif self.short_crossunder_med:
                if self.med_crossunder_long and self.df["Momentum"][i] < 0:
                    if True:
                        self.trades.append({
                            "type" : "short",
                            "bar_index": i if i == len(self.df) - 1 else i + 1,
                            "entry_price" : self.df["Open"][i] if i == len(self.df) - 1 else self.df["Open"][i+1]
                        })
                    self.short_crossunder_med = self.med_crossunder_long = False # Resetting generated trade conditions

    def test(self):
        # backtest function is used to backtest the trades
        self.max_winners_in_a_row, self.max_losers_in_a_row, self.break_evens = backtest(self.df, len(self.df), self.trades, self.tp, self.sl, self.profits, self.losses, even=self.even)
        for trade in self.profits:
            trade["result"] = "win"
        for trade in self.losses:
            trade["result"] = "loss"
        for trade in self.break_evens:
            trade["result"] = "even"

        self.trades = self.profits + self.losses + self.break_evens
        self.trades.sort(key=lambda t:t["bar_index"])


    def results(self):
        self.long_losses = [loss for loss in self.losses if loss["type"] == "long"]
        self.short_losses = [loss for loss in self.losses if loss["type"] == "short"]

        self.long_profits = [profit for profit in self.profits if profit["type"] == "long"]
        self.short_profits = [profit for profit in self.profits if profit["type"] == "short"]

        long_trades = len(self.long_profits) + len(self.long_losses)
        short_trades = len(self.short_profits) + len(self.short_losses)

        total_trades = len(self.trades)
        total_wins = len(self.profits)
        total_losses = len(self.losses)
        even_trades = len(self.break_evens)

        # win_rate = (total_wins / (total_wins + total_losses)) * 100
        win_rate = (total_wins / total_trades) * 100

        total_wins = total_wins + even_trades
        # win_rate_with_evens = (total_wins / (total_wins + total_losses)) * 100
        win_rate_with_evens = (total_wins / total_trades) * 100


        msg = f"""
        + =================================================================================== +
        |                                                                                   
        |     General Info                                                                     
        |  + -------------- +                                                                   
        |                                                                                            
        |  ASSET           : {self.asset}                                                   
        |  STOP LOSS (%)   : {self.sl}                                                      
        |  TAKE PROFIT (%) : {self.tp}                                                      
        |                                                                                   
        |                                                                                   
        |     Backtest Results                                                                 
        |  + ------------------ +                                                                                                                                             
        |                                                                                   
        |   TOTAL TRADES : {total_trades}                                                   
        |   TOTAL WINS   : {total_wins - even_trades}                                                     
        |   TOTAL LOSSES : {total_losses}                                                   
        |   EVEN TRADES  : {even_trades}                                                    
        |                                                                                                                                                                
        |   WIN RATE (WITHOUT EVEN TRADES ) : {round(win_rate, 2)} %                       
        |   WIN RATE (WITH EVEN TRADES )    : {round(win_rate_with_evens, 2)} %            
        |                                                                                                                                                                   
        |   LONG TARDES  : {long_trades}                                                    
        |   SHORT TRADES : {short_trades}                                                   
        |                                                                                   
        |   LONG WINS    : {len(self.long_profits)}                                         
        |   LONG LOSSES  : {len(self.long_losses)}                                          
        |   SHORT WINS   : {len(self.short_profits)}                                       
        |   SHORT LOSSES : {len(self.short_losses)}                                         
        |                                                                                   
        |                                                                                   
        + =================================================================================== +
        """

       

        print(msg)
        with open("msg.txt", "w") as f:
            f.write(msg)

        with open("trades.txt", "w") as f:
            data = f"""
            Trades taken
            _____________

        {json.dumps(self.trades, indent=4)}

            details
            ___________

        Long Trades won:

        {json.dumps(self.long_profits, indent=4)}

        Short Trades Won:

        {json.dumps(self.short_profits, indent=4)}

        Even Trades:

        {json.dumps(self.break_evens, indent=4)}

        Long Trades lost:

        {json.dumps(self.long_losses, indent=4)}

        Short Trades lost:

        {json.dumps(self.short_losses, indent=4)}
        
            """

            f.write(data)
            print("[+] Backtest data written to file trades.txt...")


  
  
 
