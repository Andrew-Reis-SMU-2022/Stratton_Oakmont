import xlsxwriter
import pandas as pd
import datetime



def get_color_code(total_profit, best_profit, worst_profit):
    if total_profit > best_profit * 3.0 / 4.0:
        return '#2D962C'
    elif total_profit > best_profit * 2.0 / 4.0:
        return '#3ABD3A'
    elif total_profit > best_profit * 1.0 / 4.0:
        return '#45DC45'
    elif total_profit > 0:
        return '#50FB50'
    elif total_profit < worst_profit * 3.0 / 4.0:
        return '#A62F2F'
    elif total_profit < worst_profit * 2.0 / 4.0:
        return '#CA3B3B'
    elif total_profit < worst_profit * 1.0 / 4.0:
        return '#E54242'
    elif total_profit < 0:
        return '#FF5858'

def write_to_heatmap(df_output, best_performer, worst_performer, MIN_PREMIUM, MAX_PREMIUM, PREMIUM_INCREMENT):

    df_output = pd.DataFrame(df_output)

    workbook = xlsxwriter.Workbook('output/heatmap.xlsx')
    worksheet = workbook.add_worksheet('heatmap')

    worksheet.write(0, 0, 'Strike')
    worksheet.write(0, 1, 'Monday')
    worksheet.write(0, 2, 'Tuesday')
    worksheet.write(0, 3, 'Wednesday')
    worksheet.write(0, 4, 'Thursday')

    cell_format = workbook.add_format()

    premium = MIN_PREMIUM
    row = 1
    while premium < MAX_PREMIUM + 0.01:
        worksheet.write(row, 0, premium)
        for i in range(len(df_output.index)):
            if df_output['testing_premium'][i] == premium:
                if df_output['purchase_day'][i] == 'Monday':
                    worksheet.write(row, 1, df_output['total_profit'][i],
                                    workbook.add_format({'bg_color': get_color_code(df_output['total_profit'][i],
                                                                                    best_performer['total_profit'],
                                                                                    worst_performer['total_profit']),
                                                         'num_format': '$#,##0.00_);($#,##0.00)'}))
                elif df_output['purchase_day'][i] == 'Tuesday':
                    worksheet.write(row, 2, df_output['total_profit'][i],
                                    workbook.add_format({'bg_color': get_color_code(df_output['total_profit'][i],
                                                                                    best_performer['total_profit'],
                                                                                    worst_performer['total_profit']),
                                                         'num_format': '$#,##0.00_);($#,##0.00)'}))
                elif df_output['purchase_day'][i] == 'Wednesday':
                    worksheet.write(row, 3, df_output['total_profit'][i],
                                    workbook.add_format({'bg_color': get_color_code(df_output['total_profit'][i],
                                                                                    best_performer['total_profit'],
                                                                                    worst_performer['total_profit']),
                                                         'num_format': '$#,##0.00_);($#,##0.00)'}))
                elif df_output['purchase_day'][i] == 'Thursday':
                    worksheet.write(row, 4, df_output['total_profit'][i],
                                    workbook.add_format({'bg_color': get_color_code(df_output['total_profit'][i],
                                                                                    best_performer['total_profit'],
                                                                                    worst_performer['total_profit']),
                                                         'num_format': '$#,##0.00_);($#,##0.00)'}))

        row += 1
        premium += PREMIUM_INCREMENT

    workbook.close()
