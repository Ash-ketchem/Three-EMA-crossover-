import datetime

today =  datetime.datetime.now()

paramaters = {

    "asset" : "ETH-USD",
    "time_frame" : "5m",
    "tp" : 0.5,
    "sl" : 0.4,
    "ema_list" : [9, 21, 55], # [short_ema, med_ema, high_ema]
    "max_trades" : 5,
    "time_period_int" : 60,
    "training_period" : {
        "start" : today - datetime.timedelta(days=59),
        "end" : today- datetime.timedelta(days=29)
        }
}
