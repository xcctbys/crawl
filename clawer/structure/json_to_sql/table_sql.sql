CREATE TABLE IndustryCommerceMainperson ( id INT NOT NULL PRIMARY KEY,register_num CHAR(50),name CHAR(30),position CHAR(20))

CREATE TABLE IndustryCommerceBranch ( id CHAR(20),register_num CHAR(50),branch_name CHAR(100),register_gov CHAR(50))

CREATE TABLE EnterAnnualReport ( register_num CHAR(50),report_year INT,publicity_date DATE)

CREATE TABLE YearReportShareholder ( year_report_id CHAR(20),register_num CHAR(50),shareholder CHAR(100),subscription_type CHAR(100),subscription_time DATE,subscription_money_amount FLOAT,paid_money_amount FLOAT,paid_date DATE,paid_type CHAR(100))

CREATE TABLE YearReportWarrandice ( year_report_id CHAR(20),register_num CHAR(50),creditor CHAR(100),debtor CHAR(30),main_creditor_right CHAR(30),main_creditor_right_amount FLOAT,guarantee_duration CHAR(30),guarantee_type CHAR(30),warrandice_scope CHAR(100))

CREATE TABLE YearReportOnline ( year_report_id CHAR(20),register_num CHAR(50),online_type CHAR(100),ent_name CHAR(50),url TEXT)

CREATE TABLE YearReportAssets ( year_report_id INT,register_num CHAR(50),asset_all FLOAT,owner_asset FLOAT,business_income FLOAT,main_business_income FLOAT,profit FLOAT,tax FLOAT,debts FLOAT)

CREATE TABLE YearReportInvestment ( year_report_id CHAR(20),register_num CHAR(50),invest_enter_name CHAR(50),ent_code CHAR(50))

CREATE TABLE Basic ( register_num CHAR(50),ent_name CHAR(50),ent_type CHAR(100),register_capital FLOAT,establish_date DATE,place CHAR(100),time_start DATA,time_end DATA,register_gov CHAR(50),register_status CHAR(50),check_date DATE,business_scope TEXT)

CREATE TABLE YearReportSharechange ( year_report_id CHAR(20),register_num CHAR(50),shareholder CHAR(100),shares_before FLOAT,shares_after FLOAT)

