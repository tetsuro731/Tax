 
"""
税金計算用のclassを定義する
令和2年における最新版
"""
class Tax:
    def __init__(self, gross_salary, partner = 0, high_school_student = 0, college_student = 0, handicapped = 0, rebate_contribution_rate = 0.04, health_insurance_premium_rate = 0.0987):

        self.gross_salary = gross_salary #収入
        self.partner = partner #配偶者の有無
        self.high_school_student = high_school_student #高校生の扶養がいるか
        self.college_student = college_student #大学生の扶養がいるか
        self.handicapped = handicapped #障害者か
        # 免除保険料率. 2.4〜5.0％の範囲で決まる. デフォルトは4.0%
        #年齢と共に上がる傾向にあり、20~30~40~50代でだいたい3.5~4.0~4.5~5.0%くらいを推移する
        self.rebate_contribution_rate = rebate_contribution_rate
        # 健康保険料率. デフォルトは東京の場合は9.87%
        self.health_insurance_premium_rate = health_insurance_premium_rate

        self.income_tax_rate = 0 #income()で代入する. ふるさと納税の計算で使い回す
        self.income = self.income() #incomeは何度も使うので変数に入れておく

    def income(self):
        """
        給与所得控除の計算, 収入を引数として控除額を返す
        2020年以降は控除が10万減額し、所得税で10万増えたので実質変わらない
        ただし、850万以上は給与所得控除の額が減ったで実質的には増税
        """
        employment_income_deduction = 0

        if self.gross_salary < 550000:
            employment_income_deduction = self.gross_salary

        elif self.gross_salary <1800000:
            employment_income_deduction = self.gross_salary * 0.4 - 100000

        elif self.gross_salary <3600000:
            employment_income_deduction = self.gross_salary*0.3 + 80000

        elif self.gross_salary <6600000:
            employment_income_deduction = self.gross_salary*0.2 + 440000

        elif self.gross_salary <8500000:
            employment_income_deduction = self.gross_salary*0.1 + 1100000

        else:
            employment_income_deduction = 1950000

        income = self.gross_salary - employment_income_deduction
        return income

    def social_insurance_premium(self):
        """
        保険料の計算
        保険料率 ＝ 健康保険料率/2
        + (厚生年金保険料率18.3%-免除保険料率)/2
        + 雇用保険料率0.3%
        """
        # 保険料率
        insurance_premium_rate = (self.health_insurance_premium_rate)/2 \
                                 + (0.183 - self.rebate_contribution_rate)/2 \
                                 + 0.003

        # 社会保険料 = 年収 x 保険料率
        social_insurance_premium = self.gross_salary*insurance_premium_rate
        return social_insurance_premium

    def spousal_deduction(self):
        """
        配偶者控除の計算
        """
        spousal_deduction = 0
        if self.income <= 9000000:
            spousal_deduction = 380000

        elif self.income <= 9500000:
            spousal_deduction = 260000

        elif self.income <= 10500000:
            spousal_deduction = 130000
        return spousal_deduction

    def income_tax(self):
        """
        所得税の計算
        """

        # 所得税における扶養控除
        dependents_deduction = self.high_school_student * 480000 + self.college_student * 630000
        # 所得税における障害者控除
        handicapped_deduction = self.handicapped * 260000
        # 基礎控除、2019年までは一律38万円だったが、2020年からは48万円に。ただし2000万を超えると段階的に減る
        basic_deduction = 0
        if self.income < 24000000:
            basic_deduction = 480000
        elif self.income < 24500000:
            basic_deduction = 320000
        elif self.income < 25000000:
            basic_deduction = 160000

        # 所得税の対象となる金額、所得から控除や保険料を引いたもの
        target_of_income_tax = (self.income \
                                - self.social_insurance_premium() \
                                - self.spousal_deduction() \
                                - dependents_deduction \
                                - handicapped_deduction \
                                - basic_deduction)
        # 年収別の所得税率と控除額
        if target_of_income_tax < 1950000:
            self.income_tax_rate = 0.05
            deduction = 0

        elif target_of_income_tax < 3300000:
            self.income_tax_rate = 0.1
            deduction = 97500

        elif target_of_income_tax < 6950000:
            self.income_tax_rate = 0.2
            deduction = 427500

        elif target_of_income_tax < 9000000:
            self.income_tax_rate = 0.23
            deduction = 636000

        elif target_of_income_tax < 18000000:
            self.income_tax_rate = 0.33
            deduction = 1536000

        elif target_of_income_tax < 40000000:
            self.income_tax_rate = 0.40
            deduction = 2796000

        else:
            self.income_tax_rate = 0.45
            deduction = 479.6

        # 所得税の計算
        income_tax = target_of_income_tax * self.income_tax_rate - deduction
        # 所得税がマイナスにになった場合はゼロにする
        if income_tax <= 0:
            income_tax = 0
        return income_tax

    def inhabitant_tax(self):
        """
        住民税の計算, 課税所得を引数に住民税を計算する
        """

        # 住民税における扶養控除
        dependents_deduction = self.high_school_student * 330000 + self.college_student * 450000
        # 住民税における障害者控除
        handicapped_deduction = self.handicapped * 270000
        # 基礎控除、所得税と同様2020年から変更
        basic_deduction = 0
        if self.income < 24000000:
            basic_deduction = 430000
        elif self.income < 24500000:
            basic_deduction = 190000
        elif self.income < 25000000:
            basic_deduction = 150000

        # 所得から各種控除、基礎控除（43万円）を引き、税率10%をかける
        # さらに均等割5000円を足して、調整控除2500円を引く
        inhabitant_tax = (self.income
                          - self.social_insurance_premium()
                          - self.spousal_deduction()
                          - dependents_deduction
                          - handicapped_deduction
                          - basic_deduction) * 0.1 + 5000 - 2500

        # 計算した住民税がマイナスになった場合はゼロとする
        if inhabitant_tax <=0:
            inhabitant_tax = 0
        return inhabitant_tax

    def net_salary(self):
        """
        手取りの計算、収入から所得税、住民税、社会保険料を引く
        """
        total_tax = self.inhabitant_tax() + self.income_tax()
        net_salary = self.gross_salary - total_tax - self.social_insurance_premium()
        return net_salary

    def max_hurusato_donation(self):
        """
        ふるさと納税で自己負担2000円で全額控除される上限の計算
        言い換えるとreturnの金額から2000円引いたものが所得税および住民税から控除される
        """
        # 住民税所得割額(=住民税)から計算する
        # ふるさと納税控除額の上限
        hurusato_deduction = self.inhabitant_tax() * 0.2

        # (控除金額) =（寄附金額-2000）×（90％-所得税の税率×1.021）
        # (寄付金額) = (控除金額)/(90％-所得税の税率×1.021)+2000
        max_hurusato_donation = hurusato_deduction / (0.9 - self.income_tax_rate * 1.021) + 2000
        return max_hurusato_donation
