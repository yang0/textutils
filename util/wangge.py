
def makeWeb(initMoney, initPrice, grid, level, reservation, acceleration):
    for i in range(0,level):
        inPrice = initPrice - i*(initPrice*grid)
        outPrice = inPrice + (initPrice*grid)
        inMoney = initMoney + i*acceleration*initMoney
        profit_rate = grid/(1-grid*i)
        profit = inMoney * profit_rate
        outMoney = inMoney + profit
        

        print(f'买入价：{inPrice}, 卖出价：{outPrice}, 买入金额：{inMoney}, 卖出金额:{outMoney}, 盈利：{profit}, 盈利比例:{profit_rate}')



makeWeb(10000, 1, 0.05, 7, 0.05, 0.07)