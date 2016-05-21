CREATE TABLE IndustryCommerceMainperson ( id INT,company_key CHAR(50),name CHAR(30),position CHAR(20));

CREATE TABLE IndustryCommerceBranch ( id CHAR(20),company_key CHAR(50),branch_name CHAR(100),register_gov CHAR(50));

CREATE TABLE EnterAnnualReport ( company_key CHAR(50),report_year INT,publicity_date DATE);

CREATE TABLE YearReportShareholder ( year_report_id CHAR(20),paid_time DATE,company_key CHAR(50),shareholder CHAR(100),subscription_type CHAR(100),subscription_time DATE,subscription_money_amount CHAR(20),paid_money_amount CHAR(20),paid_date DATE,paid_type CHAR(100),subscription_amount CHAR(20));

CREATE TABLE YearReportWarrandice ( year_report_id CHAR(20),company_key CHAR(50),creditor CHAR(100),debtor CHAR(30),main_creditor_right CHAR(30),main_creditor_right_amount CHAR(20),guarantee_duration CHAR(30),guarantee_type CHAR(30),fullfill_debt_duration CHAR(30),warrandice_scope CHAR(100));

CREATE TABLE YearReportOnline ( year_report_id CHAR(20),company_key CHAR(50),online_type CHAR(100),ent_name CHAR(50),url TEXT);

CREATE TABLE YearReportAssets ( year_report_id INT,company_key CHAR(50),asset_all CHAR(20),owner_asset CHAR(20),business_income CHAR(20),main_business_income CHAR(20),profit CHAR(20),tax CHAR(20),debts CHAR(20));

CREATE TABLE YearReportInvestment ( year_report_id CHAR(20),company_key CHAR(50),invest_enter_name CHAR(50),ent_code CHAR(50));

CREATE TABLE Basic ( company_key CHAR(50),register_num CHAR(50),enter_name CHAR(50),enter_type CHAR(100),register_capital CHAR(20),establish_date DATE,place CHAR(100),time_start DATE,time_end DATE,register_gov CHAR(50),check_status CHAR(50),check_date DATE,business_scope TEXT);

CREATE TABLE YearReportSharechange ( year_report_id CHAR(20),company_key CHAR(50),shareholder CHAR(100),shares_before CHAR(20),shares_after CHAR(20));

