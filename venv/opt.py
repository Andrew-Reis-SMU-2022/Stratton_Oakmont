TESTING_WIDTH = 1.0
NUM_CONTRACTS = 1

def calc_profit(weeks_list, sell_90, testing_premium, purchase_day):
    total_profit = 0
    max_loss = 0
    max_profit = 0
    num_profitable_weeks = 0
    num_unprofitable_weeks = 0
    for week in weeks_list:
        for day in week.days_list:
            if day.weekday_str == purchase_day and len(day.call_option_chain['strike']) != 0:
                try:
                    profit = day.calc_profit(week.days_list[-1].day_close, week.days_list[-1].day_high,
                                             week.days_list[-1].day_low, sell_90, testing_premium, TESTING_WIDTH, NUM_CONTRACTS)
                except:
                    break

                if profit <= TESTING_WIDTH * 100 * NUM_CONTRACTS:
                    total_profit += profit
                    
                    if profit > 0:
                        num_profitable_weeks += 1
                    elif profit < 0:
                        num_unprofitable_weeks += 1
                    
                    if total_profit < max_loss:
                        max_loss = total_profit
                    elif total_profit > max_profit:
                        max_profit = total_profit
    
    return {'total_profit': total_profit, 'max_loss': max_loss, 'max_profit': max_profit, 
            'profitable_weeks': num_profitable_weeks, 'unprofitable_weeks': num_unprofitable_weeks}