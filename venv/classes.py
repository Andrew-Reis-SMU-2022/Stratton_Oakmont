class Day:
    def __init__(self, date, open, close, high, low):
        self.date = date
        self.day_open = open
        self.day_close = close
        self.day_high = high
        self.day_low = low
        self.put_option_chain = {'strike': [], 'premium': []}
        self.call_option_chain = {'strike': [], 'premium': []}

        if date.weekday() == 0:
            self.weekday_str = 'Monday'
        elif date.weekday() == 1:
            self.weekday_str = 'Tuesday'
        elif date.weekday() == 2:
            self.weekday_str = 'Wednesday'
        elif date.weekday() == 3:
            self.weekday_str = 'Thursday'
        elif date.weekday() == 4:
            self.weekday_str = 'Friday'

    def data_cleansing(self):
        for i in range(1, len(self.call_option_chain['strike'])):
            delta = self.call_option_chain['strike'][i] - self.call_option_chain['strike'][i - 1]
            if delta <= 0 or delta > 2.5:
                self.call_option_chain['strike'] = self.call_option_chain['strike'][:i]
                self.call_option_chain['premium'] = self.call_option_chain['premium'][:i]
                break

        for i in range(1, len(self.put_option_chain['strike'])):
            delta = self.put_option_chain['strike'][i] - self.put_option_chain['strike'][i - 1]
            if delta <= 0 or delta > 2.5:
                self.put_option_chain['strike'] = self.put_option_chain['strike'][:i]
                self.put_option_chain['premium'] = self.put_option_chain['premium'][:i]
                break

        self.put_option_chain['strike'].reverse()
        self.put_option_chain['premium'].reverse()

    def calc_profit(self, week_close, friday_high, friday_low, sell_90, testing_premium, testing_width, num_contracts):
        call_buy_index = 0
        while self.day_close > self.call_option_chain['strike'][call_buy_index]:
            call_buy_index += 1

        try:
            call_sell_index = self.call_option_chain['strike'].index(self.call_option_chain['strike'][call_buy_index] + testing_width)
        except ValueError:
            call_buy_index += 1
            call_sell_index = self.call_option_chain['strike'].index(self.call_option_chain['strike'][call_buy_index] + testing_width)

        self.call_premium = self.call_option_chain['premium'][call_buy_index] - self.call_option_chain['premium'][call_sell_index]
        while self.call_premium > testing_premium / 2.0:
            call_buy_index += 1
            call_sell_index += 1
            self.call_premium = self.call_option_chain['premium'][call_buy_index] - self.call_option_chain['premium'][call_sell_index]

        put_buy_index = 0
        while self.day_close < self.put_option_chain['strike'][put_buy_index]:
            put_buy_index += 1
        try:
            put_sell_index = self.put_option_chain['strike'].index(self.put_option_chain['strike'][put_buy_index] - testing_width)
        except ValueError:
            put_buy_index += 1
            put_sell_index = self.put_option_chain['strike'].index(self.put_option_chain['strike'][put_buy_index] - testing_width)

        self.put_premium = self.put_option_chain['premium'][put_buy_index] - self.put_option_chain['premium'][put_sell_index]
        while self.put_premium > testing_premium / 2.0:
            put_buy_index += 1
            put_sell_index += 1
            self.put_premium = self.put_option_chain['premium'][put_buy_index] - self.put_option_chain['premium'][put_sell_index]

        self.total_premium = self.call_premium + self.put_premium
        self.buy_put_strike = self.put_option_chain['strike'][put_buy_index]
        self.sell_put_strike = self.put_option_chain['strike'][put_sell_index]
        self.buy_call_strike = self.call_option_chain['strike'][call_buy_index]
        self.sell_call_strike = self.call_option_chain['strike'][call_sell_index]

        if ((friday_high - self.sell_call_strike) / self.sell_call_strike >= 0.0035 or \
                (friday_low - self.sell_put_strike) / self.sell_put_strike <= -0.0035) and sell_90:
            self.profit = (0.9 - self.total_premium) * 100 * num_contracts
        elif week_close >= self.buy_put_strike and week_close <= self.buy_call_strike:
            self.profit = -self.total_premium  * 100 * num_contracts
        elif week_close > self.buy_call_strike and week_close < self.sell_call_strike:
            self.profit = ((week_close - self.buy_call_strike) - self.total_premium) * 100 * num_contracts
        elif week_close < self.buy_put_strike and week_close > self.sell_put_strike:
            self.profit = ((self.buy_put_strike - week_close) - self.total_premium) * 100 * num_contracts
        elif week_close >= self.sell_call_strike or week_close <= self.sell_put_strike:
            self.profit = (testing_width - self.total_premium) * 100 * num_contracts
        else:
            raise Exception("Something went horribly wrong...")

        return self.profit


class Week:
    def __init__(self):
        self.days_list = []