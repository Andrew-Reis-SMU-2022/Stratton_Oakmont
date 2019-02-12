import pandas as pd
import xlsxwriter
import datetime
import os
import pickle
from classes import Day
from classes import Week
from opt import calc_profit
from write import write_to_heatmap

MIN_PREMIUM = 0.2
MAX_PREMIUM = 0.85
PREMIUM_INCREMENT = 0.05

testing_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
first_year = int(input("Enter the beginning year: "))
last_year = int(input("Enter the last year: "))
testing_years = range(first_year, last_year + 1)
pickle_answer = input('Pickle? ')
answer_90 = input('Do you want to sell at .90? ')
if answer_90.lower() == 'yes':
    sell_90 = True
else:
    sell_90 = False

weeks_list = []
for file in os.listdir('underlying_daily_performance'):
    df_spy_performance = pd.read_csv(f'underlying_daily_performance/{file}')
    new_week = True
    for i in range(1, len(df_spy_performance.index)):
        if int(df_spy_performance['Date'][i].split('-')[0]) in testing_years:
            current_date = datetime.date(int(df_spy_performance['Date'][i].split('-')[0]), int(df_spy_performance['Date'][i].split('-')[1]),
                                         int(df_spy_performance['Date'][i].split('-')[2]))
            next_date = datetime.date(int(df_spy_performance['Date'][i + 1].split('-')[0]), int(df_spy_performance['Date'][i + 1].split('-')[1]),
                                      int(df_spy_performance['Date'][i + 1].split('-')[2]))
            if new_week:
                current_week = Week()
                new_week = False
            current_week.days_list.append(Day(current_date, float(df_spy_performance['Open'][i]), float(df_spy_performance['Close'][i]), float(df_spy_performance['High'][i]), float(df_spy_performance['Low'][i])))
            if new_week == False and next_date - current_date >= datetime.timedelta(days=3):
                weeks_list.append(current_week)
                new_week = True

if pickle_answer.lower() == 'no':
    for file in os.listdir('option_price_data'):
        df_options = pd.read_csv(f'option_price_data/{file}')
        for i in range(1, len(df_options.index)):
            buy_date = datetime.date(int(df_options['date'][i].split('/')[0]), int(df_options['date'][i].split('/')[1]),
                                     int(df_options['date'][i].split('/')[2]))
            exp_date = datetime.date(int(df_options['exdate'][i].split('/')[0]),
                                     int(df_options['exdate'][i].split('/')[1]),
                                     int(df_options['exdate'][i].split('/')[2]))
            for week in weeks_list:
                for day in week.days_list:
                    if buy_date == day.date and (exp_date == week.days_list[-1].date or exp_date == week.days_list[-1].date + datetime.timedelta(days=1)):
                        print(exp_date)
                        if df_options['cp_flag'][i] == 'C' and not float(df_options['strike_price'][i])/ 1000 in day.call_option_chain['strike']:
                            if float(df_options['best_offer'][i]) >= .02 and float(df_options['best_offer'][i] <= 3.0):
                                day.call_option_chain['strike'].append(float(df_options['strike_price'][i]) / 1000)
                                day.call_option_chain['premium'].append(float(df_options['best_offer'][i]))
                        elif df_options['cp_flag'][i] == 'P' and not float(df_options['strike_price'][i])/ 1000 in day.put_option_chain['strike']:
                            if float(df_options['best_offer'][i]) >= .02 and float(df_options['best_offer'][i] <= 3.0):
                                day.put_option_chain['strike'].append(float(df_options['strike_price'][i]) /1000)
                                day.put_option_chain['premium'].append(float(df_options['best_offer'][i]))

    for week in weeks_list:
        for day in week.days_list:
            if len(day.call_option_chain['strike']) > 1 and len(day.put_option_chain['strike']) > 1:
                day.data_cleansing()

    with open(f'pickle_data/{testing_years[0]} - {testing_years[-1]}.pickle', 'wb') as pickle_out:
        pickle.dump(weeks_list, pickle_out)

if pickle_answer.lower() == 'yes':
    weeks_list = []
    with open(f'pickle_data/{testing_years[0]} - {testing_years[-1]}.pickle', 'rb') as pickle_in:
        weeks_list = pickle.load(pickle_in)

best_performer = {'total_profit': 0, 'max_loss': 0, 'max_profit': 0, 'profitable_weeks': 0, 'unprofitable_weeks': 0,
                  'testing_premium': 0, 'purchase_day': ''}
worst_performer = {'total_profit': 0, 'max_loss': 0, 'max_profit': 0, 'profitable_weeks': 0, 'unprofitable_weeks': 0,
                   'testing_premium': 0, 'purchase_day': ''}
df_output = {'total_profit': [], 'max_loss': [], 'max_profit': [], 'profitable_weeks': [], 'unprofitable_weeks': [],
             'testing_premium': [], 'purchase_day': []}
testing_premium = MIN_PREMIUM
while testing_premium < MAX_PREMIUM + 0.01:
    for purchase_day in testing_days:
        output_dict = calc_profit(weeks_list[:], sell_90, testing_premium, purchase_day)

        print(f'\nTesting Premium: {testing_premium}')
        print(f'Purchase Day: {purchase_day}')
        print(f'Total Profit: {output_dict["total_profit"]:,.2f}')
        print(f'Max loss: {output_dict["max_loss"]:,.2f}')
        print(f'Max Profit: {output_dict["max_profit"]:,.2f}')
        print(f'Profitable weeks: {output_dict["profitable_weeks"]}')
        print(f'Unprofitable weeks: {output_dict["unprofitable_weeks"]}')

        df_output['total_profit'].append(output_dict['total_profit'])
        df_output['max_loss'].append(output_dict['max_loss'])
        df_output['max_profit'].append(output_dict['max_profit'])
        df_output['profitable_weeks'].append(output_dict['profitable_weeks'])
        df_output['unprofitable_weeks'].append(output_dict['unprofitable_weeks'])
        df_output['testing_premium'].append(testing_premium)
        df_output['purchase_day'].append(purchase_day)

        if output_dict['total_profit'] > best_performer['total_profit']:
            best_performer['total_profit'] = output_dict['total_profit']
            best_performer['max_profit'] = output_dict['max_profit']
            best_performer['max_loss'] = output_dict['max_loss']
            best_performer['profitable_weeks'] = output_dict['profitable_weeks']
            best_performer['unprofitable_weeks'] = output_dict['unprofitable_weeks']
            best_performer['testing_premium'] = testing_premium
            best_performer['purchase_day'] = purchase_day
        elif output_dict['total_profit'] < worst_performer['total_profit']:
            worst_performer['total_profit'] = output_dict['total_profit']
            worst_performer['max_profit'] = output_dict['max_profit']
            worst_performer['max_loss'] = output_dict['max_loss']
            worst_performer['profitable_weeks'] = output_dict['profitable_weeks']
            worst_performer['unprofitable_weeks'] = output_dict['unprofitable_weeks']
            worst_performer['testing_premium'] = testing_premium
            worst_performer['purchase_day'] = purchase_day

    testing_premium += PREMIUM_INCREMENT

print('\nBest Performer')
print(f'\nTesting Premium: {best_performer["testing_premium"]}')
print(f'Testing Purchase Day: {best_performer["purchase_day"]}')
print(f'Total Profit: {best_performer["total_profit"]:,.2f}')
print(f'Max loss: {best_performer["max_loss"]:,.2f}')
print(f'Max Profit: {best_performer["max_profit"]:,.2f}')
print(f'Profitable weeks: {best_performer["profitable_weeks"]}')
print(f'Unprofitable weeks: {best_performer["unprofitable_weeks"]}')

print('\nWorst Performer')
print(f'\nTesting Premium: {worst_performer["testing_premium"]}')
print(f'Testing Purchase Day: {worst_performer["purchase_day"]}')
print(f'Total Profit: {worst_performer["total_profit"]:,.2f}')
print(f'Max loss: {worst_performer["max_loss"]:,.2f}')
print(f'Max Profit: {worst_performer["max_profit"]:,.2f}')
print(f'Profitable weeks: {worst_performer["profitable_weeks"]}')
print(f'Unprofitable weeks: {worst_performer["unprofitable_weeks"]}')

write_to_heatmap(df_output, best_performer, worst_performer, MIN_PREMIUM, MAX_PREMIUM, PREMIUM_INCREMENT)
