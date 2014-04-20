

****************************************************************
******* ECON 131 - Econometrics and Data Analysis **************
*********************** Fall 2013 ******************************
****************************************************************

****************************************************************
****************** Introduction to Stata ***********************
****************************************************************




/*
****************************************************************
************************** Outline *****************************

PART 1. - Getting Data into Stata

PART 2. - Inspecting the Data

PART 3. - Analyzing the Data through Descriptive Statistics
		PART 3.1 - Command SUMMARIZE
		PART 3.2 - Command TABULATE
		PART 3.3 - Command CORRELATE
		PART 3.4 - Option IF
		PART 3.5 - Option BY
		
PART 4. - Modifying the Data
		PART 4.1 - Creating New Variables
				   PART 4.1.a - Create a Generic Variable
				   PART 4.1.b - Create a Dummy Variable
				   PART 4.1.c - Create a Categorical Variable
				   PART 4.1.d - Create a Variable using the command EGEN				   
		PART 4.2 - Deleting Variables
		
PART 5. - Graphs
		PART 5.1 - Histograms
		PART 5.2 - Scatterplots
		PART 5.3 - Normal Distribution
		PART 5.4 - Saving Graphs
		
PART 6. - Getting Help

****************************************************************
*/


* Do-files are a way to stack all the commands together.
* They are HIGHLY recommended compared to the use of the Command Window because they allow you to KEEP TRACK of everything you do.

* If you want to include a comment in a do-file, use an asterisk at the beginning of the line.
* Indeed, Stata does not execute lines that start with an asterisk.
* If you want to comment more than one line, include the lines in between /* ... */


* Use the command CD to set a default directory that you want Stata to get files from. 
* This is not necessary, however. If you don't specify a directory path at the beginning, you will simply have to specify it whenever you "call"
* a file through your commands.
* An example would be:
cd "C:\Users\Gabriella\STATA\MxFLS"

* You can open a log-file at the beginning of your work.
/* A log-file allows to save all the work that will appear in the Results Window. You will use the command LOG USING at the beginning of your
work and will use LOG CLOSE at the end. Everything you run in between LOG USING and LOG CLOSE will be saved in a text file that you can review 
even when Stata is closed. 
*/
log using econ131_stata_tutorial, replace text
* The option REPLACE allows to overwrite an existing log-file with the same name (useful when you plan to run the same do-file multiple times).
* If you haven't specified a directory path through the CD command, you will have to specify the path before the name of the file. 
* An example would be:
log using "C:\Users\Gabriella\STATA\MxFLS\econ131_stata_tutorial", replace text



***************************************
*** PART 1. Getting Data into Stata ***
***************************************

* Always start a do-file with the command CLEAR. It closes any dataset that may still be open.
clear

* If your data are in Stata format (that is, .dta), you can open them through the command USE. 
use mexican_family_life_survey_2002.dta
* If you haven't specified a directory path through the CD command, you will have to specify the path before the name of the file. 
* An example would be:
use "C:\Users\Gabriella\STATA\MxFLS\mexican_family_life_survey_2002.dta"


* Alternatively, if you have data in Excel, use the command INSHEET to upload the data from Excel to Stata. Notice that, before doing this,
* you will have to save (in Excel) your data in .csv format.
insheet using mexican_family_life_survey_2002.csv
* Again, if you haven't specified a directory path, you will have to specify the path before the name of the file. 
* An example would be:
insheet using "C:\Users\Gabriella\STATA\MxFLS\mexican_family_life_survey_2002.csv"
* Once you have imported your Excel data into Stata through the command INSHEET, you can save them in Stata format using the command SAVE.
save mexican_family_life_survey_2002.dta, replace 
* Again, the option REPLACE allows you to overwrite an existing file with the same name (useful when you plan to save the file multiple times).
* If you haven't specified a directory path through the CD command, you will have to specify the path before the name of the file. 
* An example would be:
save "C:\Users\Gabriella\STATA\MxFLS\mexican_family_life_survey_2002.dta", replace 



***********************************
*** PART 2. Inspecting the Data ***
***********************************

* Inspect the data. The command BROWSE will open up the Browse Window.
browse
* You can also browse only some of the variables.
browse education age

* Count the number of observations in the dataset using the command COUNT.
count

* Get a description of the variables in the dataset using the command DESCRIBE. Notice how a "variable label" helps you understnding which
* information the variable contains.
* You can get a description of all of the variables through DESCRIBE:
describe
* Or of only some of them (for instance, education and age), by specifying which variables after DESCRIBE.
describe education age

* Use the command LIST to obtain in the Results Window the values of specific variables for some or all the individuals in the dataset.
* Example 1: Obtain the age and gender of individual 15
list age gender in 15
* Example 2: Obtain the age and gender of individuals 10 to 30
list age gender in 10/30


* Understand the concept of value label.
* Often in Stata we save information in numeric format even for variables that are not numeric in nature. For instance, to indicate the gender
* of an individual, instead of having a variable that equals either "Female" or "Male", we assign numbers to those categories (1=Male, 2=Female).
* We then assign a value label to the variable gender so as to remember ourselves that 1 means "Male" and 2 means "Female".
* The command LABEL LIST allows you to read which numbers correspond to each category of a variable.
describe gender
label list gender
browse gender
* Another example is education levels:
describe education
label list education
browse education
* The concept of value label is important because in the commands, when needed, you will use the numeric values rather than their meaning
* (for instance, you will use number 2 for female, rather than the word "Female").



*****************************************************************
*** PART 3. Analyzing the Data through Descriptive Statistics ***
*****************************************************************

*************************************
*** PART 3.1 -  Command SUMMARIZE ***
*************************************

* The command SUMMARIZE returns the number of observations, mean, standard deviation, minimum and maximum values of variables.
summarize income
* Can have more than one variable.
summarize income weight age
* Can obtain further summary statistics using the option DETAIL.
summarize income, detail
* Notice the difference between the mean and the median. What is this due to?


************************************
*** PART 3.2 -  Command TABULATE ***
************************************

* The command TABULATE returns the frequency table of a variable. It is best suited for those variables that can only take a limited number of 
* values. 
tabulate gender
tabulate education
tabulate age
tab worked
* You can also create a cross-tabulation of two variables. For instance, you may be interested in how educational levels differ across males
* and females.
tabulate education gender
* The command TABULATE only gives you the number of observations with a specific characteristic. If you want to know their frequency,
* you have to use the options ROW or COLUMN. 
tabulate education gender, row
tabulate education gender, column
* Another example would be looking at how the participation to the labor market varies across males and females.
tabulate worked gender,column
tabulate worked gender,row



*************************************
*** PART 3.3 -  Command CORRELATE ***
*************************************

* The command CORRELATE provides information on how two or more variables co-move. If you specify the option COVARIANCE, it will give you 
* the pairwise covariance of two or more variables.
correlate height weight, covariance  



*****************************
*** PART 3.4 -  Option IF ***
*****************************

* It is possible to run all the commands above (and many others) restricting your attention to a subset of observations, 
* according to a criterion that you specify.
* Example 1: You want to know the average income only for people above forty (not for the population in general).
summarize income if age>40
* Example 2: You want to know the average income only for people with high school or with a college degree.
summarize income if education == 6 | education == 9
* Example 3: You want to know the average weight of kids (1 to 3 years) who are males. 
summarize weight if gender==1 & age>=1 & age<=3

* Notice that above we have made use of some logical operators. Here a full list of all logical operators used in Stata:
*
*                            Operators in expressions
*
*                                                         Relational
*         Arithmetic              Logical            (numeric and string)
*    --------------------     ------------------     ---------------------
*     +   addition                ~   not               >   greater than
*     -   subtraction             !   not               <   less than
*     *   multiplication          |   or                >=  > or equal
*     /   division                &   and               <=  < or equal
*     ^   power                                         ==  equal
*                                                       ~=  not equal
*     						                            !=  not equal


*****************************
*** PART 3.5 -  Option BY ***
*****************************

* The option BY allows you to execute commands across the category you specify. The option SORT is needed to sort the category according 
* to which you are executing a command.
by gender, sort: summarize income
by age, sort: summarize weight
* Can apply more than one option at the time
by gender, sort: summarize weight if age>=5 & age<=10
by education, sort: summarize income if age>25 & age<55, detail




**********************************
*** PART 4. Modifying the Data ***
**********************************

****************************************
*** PART 4.1 -  Create New Variables ***
****************************************

* To create a new variable you will mostly use the command GENERATE. We will see below also the command EGEN, which is an extension to GENERATE.


***********************************************
*** PART 4.1.a -  Create a Generic Variable ***
***********************************************

* The variable height in the dataset measures height in centimeters. Using the fact that 1 centimeter = 0.032808399 feet, let's create a variable
* that measures height in feet.
generate height_feet = height*0.032808399



*********************************************
*** PART 4.1.b -  Create a Dummy Variable ***
*********************************************

* A dummy variable is a variable that only takes values zero or one. It is often used to indicate whether a person
* has a given characteristic (variable = 1) or not (variable = 0).

* Example 1: Create a dummy that indicates whether a person is female.
generate female = 1 if gender==2
* The above command creates a variable female which takes value 1 if gender==2, but takes value "." (that is, missing) if gender==1. However, we
* want the value of female to be zero when gender==1. We can use the command REPLACE to do this.
replace female = 0 if gender==1
* Check the result:
tabulate female
tabulate gender
* An alternative way to create the same dummy (which avoids the REPLACE step) is:
generate female = (gender==2)
* Assign a label to the new variable using the command LABEL VARIABLE:
label variable female "Variable==1 if individual is female"

* Example 2: Generate a dummy indicating whether a person has college education
label list education
generate college = (education==9)
* Assign a label to the new variable using the command LABEL VARIABLE:
label variable college "Variable==1 if individual has college education"




***************************************************
*** PART 4.1.c -  Create a Categorical Variable ***
***************************************************

* A categorical variable is a variable that takes a limited number of values, each generally indicating a category.
* For instance, we can create a variable that records age categories.
tabulate age
generate age_cat = .
replace age_cat = 1 if age<=15
replace age_cat = 2 if age>15 & age<=25
replace age_cat = 3 if age>25 & age<=35
replace age_cat = 4 if age>35 & age<=45
replace age_cat = 5 if age>45 & age<=55
replace age_cat = 6 if age>55
* Define a new value label for the variable we just created through the command LABEL DEFINE and then assign the value label to the new variable
* through the command LABEL VALUES:
label define age_cat_label 1 "Less 15" 2 "15-25" 3 "25-35" 4 "35-45" 5 "45-55" 6 "Over 55"
label values age_cat age_cat_label
* Assign a label to the new variable:
label variable age_cat "Age categories"

* We can now use the just created age categories to explore income across age categories. Notice how this is more convenient that exploring
* income for each single age.
by age_cat, sort: summarize income, detail
* Compare income of males and females in the age category 25-35 and 35-45
by gender, sort: sum income if age_cat==3, detail
by gender, sort: sum income if age_cat==4, detail


**************************************************************
*** PART 4.1.d -  Create a Variable using the Command EGEN ***
**************************************************************

* The command EGEN is an extension to the command GENERATE which allows you to create variables using a number of Stata in-built functions.
* Here we describe EGEN MEAN, which, combined with the option BY, will give you the mean of a variable across the category you specify.
* Example: Let's use EGEN MEAN to generate a variable (mean_income) that for women will take the value of "average women's income" and for 
* men the value of "average men's income". We will then use mean_income to create a new dummy variable indicating whether an
* individual's income is below the average for his group.
by gender,sort: egen mean_income = mean(income)
generate below_mean = (income < mean_income)
replace below_mean = . if income==.
label variable below_mean "Variable==1 if individual has income below the mean for his group"


*************************************
*** PART 4.2 -  Delete Variables ***
*************************************

* You can delete variables you don't need using the command DROP. Be careful though, as the DROP command cannot be undone.
generate female_duplicate = female
drop female_duplicate



**********************
*** PART 5. Graphs ***
**********************

******************************
*** PART 5.1 -  Histograms ***
******************************

* You can plot the frequency or density of data using the command HISTOGRAM.
histogram income
* The histogram just obtained doesn't look great. The reason is that the presence of outliers makes difficult reading the graph.
* Let's draw the histogram for incomes below 200,000. 
histogram income if income<200000
* If you specify the option FREQUENCY, you obtain a plot of the frequency rather than the density of your variable.
histogram income if income<200000, frequency

* You can use HISTOGRAM with the BY option to obtain an histogram for each value of the specified category.
* For instance, you may be interested in how the distribution of income changes across males and females.
histogram income if income<200000, by(gender)
* What can you conclude from the histogram we just drew? What do the commands below plot? What do they tell you?
histogram income if age>25 & age<55 & income<200000, by (gender)
histogram income if age>25 & income<150000 & (edu==3 | edu==4 | edu==6 | edu==9), by (education)
histogram income if age>25 & income<150000 & (edu==3 | edu==4 | edu==6 | edu==9) & gender==1, by (education)



********************************
*** PART 5.2 -  Scatterplots ***
********************************

* The command GRAPH TWOWAY allows you to obtain a number of different plots. As the word TWOWAY indicates, the common denominator among them
* is that you will have two variables, one whose values will be on the x-axis and one whose values will be on the y-axis.
* If you specify SCATTER after GRAPH TWOWAY, you will obtain a scatterplot.
graph twoway scatter weight  height_feet  
* You can add a title to your graph.
graph twoway  scatter weight  height_feet, title("Height and Weight")
* You can  add a linear fit of the data to the scatterplot through the command LFIT.
graph twoway (scatter weight height_feet) (lfit weight  height_feet) 
* Given the graph we just plotted, would you say that a linear fit is a good approximation for the relationship between weight and height?
* If not, why?
* A linear fit may however constitute a very good approximation for young kids. Let's see whether this is the case:
graph twoway (scatter weight height_feet) (lfit weight  height_feet) if age<2
* The presence of an outlier is impeding a clear reading. Let's restrict our attention to height_feet<4.
graph twoway (scatter weight height_feet) (lfit weight height_feet) if age<2 & height_feet<4
* Is now a linear relation a better approximation? Why?


***************************************
*** PART 5.3 -  Normal Distribution ***
***************************************

* You can use the option NORMAL together with the command HISTOGRAM to add a normal density to the graph.
histogram height_feet
histogram height_feet, normal
* The height data don't seem well described by a normal. But in class we said the opposite. What is wrong in the graph we just made?
* Let's try restricting attention to people old enough.
histogram height_feet if age>20, normal
* You may be interested in whether and how the distribution changes across males and females. Is the mean the same? What about the variance?
histogram height_feet if age>20, normal by (gender)

* Often a variable is not normally distributed, but its logarithm might. Let's try with income.
histogram income if income<200000, normal
generate log_income = log(income)
histogram log_income, normal



*********************************
*** PART 5.4 -  Saving Graphs ***
*********************************

* The easiest way for you to save graphs is to use the button SAVE GRAPH in the Graph Window menu.
* You can specify the format of your image file: the default is .gph, but you will want to use .png for higher resolution.




****************************
*** PART 6. Getting Help ***
****************************

* Are you confused about any of the commands above? Just ask Stata for help! Through the command HELP you can get a description of how the
* command works and a list of examples about the command you are interested in. Just type in HELP followed by the command you are interested in.
* When you are not sure about which specific command in Stata corresponds to the function you are looking for, you can use HELP followed by 
* a keyword rather than a command.
help cd
help log
help use
help insheet
help browse
help count
help describe
help list
help summarize
help tabulate
help correlate
help generate
help egen
help replace
help label
help drop 
help histogram
help graph

* You can also access very helpful material to learn how to use Stata using the link: http://www.ats.ucla.edu/stat/stata/
* On the Yale Statlab website, you can also find useful material from past "Introductory Stata" workshops: http://statlab.stat.yale.edu/help/workshops/ 


* Now remember to close the log file you opened at the beginning of your work through the command LOG CLOSE.
log close
