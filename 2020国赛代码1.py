import pandas as pd
import numpy as np
import math


def season(date):
    years, month = str(date)[: 4], str(date)[5: 7]
    season0 = math.ceil(int(month) / 3)
    return years + "s" + str(season0)


oriData = pd.read_excel("Q2data\\d2destroy.xlsx")

oriData["season"] = oriData["开票日期"].map(lambda x: season(x))
oriData["year"] = oriData["开票日期"].map(lambda x: int(str(x)[: 4]))
oriData["month"] = oriData["开票日期"].map(lambda x: str(x)[: 7])

oriData["taxRate"] = 100 * oriData["税额"] / oriData["金额"]
oriData.replace(np.nan, 0, inplace=True)
oriData.replace(np.inf, 0, inplace=True)
oriData["taxRate"] = oriData["taxRate"].map(lambda x: round(x))

yearList = oriData["year"].unique()
seasonList = oriData["season"].unique()
monthList = oriData["month"].unique()
companyList = oriData["企业代号"].unique()
companyMap = dict(zip(companyList, [0] * len(companyList)))

finDict = {"企业代号": companyList}

'''------------------统计税率数据 -------------------'''
taxDf = pd.DataFrame({"税率": oriData["taxRate"].unique()})
taxDf.to_csv("税率统计.csv", encoding="utf_8_sig")

'''-------------------------------------------------'''

'''------------统计分季度各企业进出帐金额 -------------'''
for eachSeason in seasonList:
    seasonDf0 = oriData.loc[(oriData["season"] == eachSeason)]
    seasonDf = seasonDf0.groupby("企业代号")
    resDf = pd.DataFrame(seasonDf.sum()[["金额"]])
    companyMap = dict(zip(companyList, [0] * len(companyList)))
    for company in seasonDf0["企业代号"].unique():

        companyMap[company] = resDf.at[company, "金额"]

    resList = [number for number in companyMap.values()]
    finDict[eachSeason] = resList
    print(eachSeason)

finDf = pd.DataFrame(finDict)
finDf.to_csv("Q2data\\季度销项发票金额.csv", encoding='utf_8_sig')

'''-------------------------------------------------'''

'''------------------统计上下游企业数量 --------------'''
for eachSeason in seasonList:
    seasonDf0 = oriData.loc[(oriData["season"] == eachSeason)]
    companyMap = dict(zip(companyList, [0] * len(companyList)))
    for company in seasonDf0["企业代号"].unique():

        companyMap[company] = len(seasonDf0.loc[(seasonDf0["企业代号"]) == company]["销方单位代号"].unique())

    resList = [number for number in companyMap.values()]
    finDict[eachSeason] = resList
    print(eachSeason)
finDf = pd.DataFrame(finDict)
finDf.to_csv("Q2data\\季度上游企业数量修改版.csv", encoding='utf_8_sig')

'''-------------------------------------------------'''

'''--------------统计发票状态数量和金额 --------------'''
for eachSeason in seasonList:
    seasonDf0 = oriData.loc[(oriData["season"] == eachSeason)]
    df1 = seasonDf0.loc[(seasonDf0["金额"] < 0)]
    companyMap = dict(zip(companyList, [0] * len(companyList)))
    for company in seasonDf0["企业代号"].unique():

        companyMap[company] = df1.loc[(df1["企业代号"]) == company]["金额"].sum()

    resList = [number for number in companyMap.values()]
    finDict[eachSeason] = resList
    print(eachSeason)
finDf = pd.DataFrame(finDict)
finDf.to_csv("Q2data\\季度进项负发票金额.csv", encoding='utf_8_sig')

'''-------------------------------------------------'''

'''----------统计发票金额前20供应商和金额量 -----------'''
yearLists = [2016, 2017, 2018, 2019, 2020]


def topName(top5yearList):
    retDict = {"企业代号": companyList}
    for year in top5yearList:
        top5List = []
        yearDf = oriData.loc[(oriData["year"]) == year]
        for company in companyList:
            companyDf = yearDf.loc[(oriData["企业代号"]) == company]
            totalMoney = companyDf["金额"].sum()
            grouped = companyDf.groupby("购方单位代号")

            resDf = pd.DataFrame(grouped.sum()[["金额"]]).sort_values("金额", ascending=False)

            top20number = list(resDf[: 20]["金额"])
            top20number += [0 for _ in range(20 - len(top20number))]
            print(top20number)
            top5List.append(sum(top20number[:5])/(totalMoney + 1))
            top20company = list(resDf.index.values)
            # top20company += [i for i in range(0, 20 - len(top20company))]
            top20company = top20company[: 5]
        retDict[year] = top5List
    rDf = pd.DataFrame(retDict)
    rDf.to_csv("Q2data\\销项前五百分比.csv", encoding="utf_8_sig")
    return retDict

# netDict = dict(zip(top20company, top20number))
# netList = [_ for _ in netDict.items()]
# netList.append(totalMoney)
#
# finDf = pd.DataFrame(companyMap)
# finDf.to_csv(str(year) + "进账发票仅金额前二十统计.csv", encoding="utf_8_sig")


topName(yearLists)


# topName2016 = topName(2016)
# topName2017 = topName(2017)
# topName2018 = topName(2018)
# topName2019 = topName(2019)
# topName2020 = topName(2020)

dict17 = []
dict18 = []
dict19 = []
dict20 = []

# for companies in companyList:
#     dict17.append(len(set(topName2016[companies]) & set(topName2017[companies])))
#     dict18.append(len(set(topName2017[companies]) & set(topName2018[companies])))
#     dict19.append(len(set(topName2018[companies]) & set(topName2019[companies])))
#     dict20.append(len(set(topName2019[companies]) & set(topName2020[companies])))

finalDict = {"企业代号": companyList,
             "16-17": dict17,
             "17-18": dict18,
             "18-19": dict19,
             "19-20": dict20}

df = pd.DataFrame(finalDict)
df.to_csv("进项发票前五名差异数.csv", encoding="utf_8_sig")

'''---------------------------------------------'''

'''----------统计分月度各企业进出帐金额 -----------'''
for eachMonth in monthList:
    companyMap = dict(zip(companyList, [0] * len(companyList)))
    monthDf0 = oriData.loc[(oriData["month"] == eachMonth)]

    for company in monthDf0["企业代号"].unique():
        companyMap[company] = monthDf0.loc[(monthDf0["企业代号"] == company)]["金额"].sum()

    resList = [number for number in companyMap.values()]
    finDict[eachMonth] = resList

finDf = pd.DataFrame(finDict)
finDf.to_csv("月份进项发票总金额.csv", encoding='utf_8_sig')

'''---------------------------------------------'''

'''-----------------半方差的计算 ----------------'''
monthlyData = pd.read_csv("Q2data\\月度销项发票金额.csv")

varList = []
for companies in companyList:
    comData = monthlyData[companies]
    for j in range(0, len(comData)):
        if comData[j]:
            comData = comData[j:]
            break
    means = comData.mean()
    arr = comData - means
    simVar = ((sum(arr[arr < 0] ** 2) / len(comData)) ** (1/2)) / means
    varList.append(simVar)
    # summed = comData.sum()
    # varList.append(summed / len(comData.index.unique()))

finDict["半方差"] = varList
retDf = pd.DataFrame(finDict)
retDf.to_csv("Q2data\\销项月平均金额.csv", encoding="utf_8_sig")

'''---------------------------------------------'''

'''-------------计算发票金额超平均次数------------'''
retList = []
for company in companyList:
    data2019 = oriData.loc[(oriData["year"] == 2019)]
    companyDf = data2019.loc[(oriData["企业代号"] == company)]
    grouped = companyDf.groupby("开票日期")
    dateData = pd.DataFrame(grouped.sum()[["金额"]])["金额"]
    stdVar = dateData.var() ** (1/2)
    means = dateData.mean()
    retList.append(len(dateData[dateData > means + 1.5 * stdVar]) + 1)

finDict["进项发票超平均次数"] = retList
retDf = pd.DataFrame(finDict)
retDf.to_csv("Q2data\\2019进项发票超平均次数.csv", encoding="utf_8_sig")
print(oriData)

'''---------------------------------------------'''

'''-----------------协方差的计算 ----------------'''
monthData = pd.read_csv("Q2data\\月度销项发票金额.csv")
covMatrix = monthData.cov() / 10 ** 6
covMatrix.to_csv("Q2data\\协方差矩阵.csv", encoding="utf_8_sig")

'''---------------------------------------------'''

'''-----------------等级分布的计算----------------'''
industryDf = pd.read_excel("Q2data\\第二问指标统计贷行业(1).xlsx")
industryList = industryDf["行业"].unique()
rankList = ["A", "B", "C", "D"]
retDict = {"行业": industryList}
for rank in rankList:
    groupList = []
    group = industryDf.loc[(industryDf["等级"] == rank)]
    numberOfCompany = len(group)
    for industry in industryList:
        groupList.append(len(group.loc[(group["行业"] == industry)]) / numberOfCompany)
    retDict[rank] = groupList

retDf = pd.DataFrame(retDict)
retDf.to_csv("Q2data\\行业等级分布按等级分.csv", encoding="utf_8_sig")
print(industryDf)

'''---------------------------------------------'''

