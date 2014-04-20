
******************************************************************
**************************** ECON 131 **************************** 
**************** ECONOMETRICS AND DATA ANALYSIS I **************** 
*************************** FALL 2013 **************************** 
******************************************************************


******************************************************************
************************** GPA Exercise **************************
******************************************************************

*cd "C:\Users\BF\Dropbox\Teaching\Stata\"

log using GPA_exercise.txt, replace text

use "gpa2.dta", clear



*************************
********* Part 1 ********
*************************

********************************
********* 1.a. to 1.d **********

summarize colgpa, detail
summarize sat, detail

regress colgpa hsperc sat

* What is the effect of a difference of 140 points in the SAT?
local sateffect = _b[sat]
local sat140 = 140 * `sateffect'
di `sat140'

* sat difference that corresponds to GPA difference of .50 for 1.d:
local satdiff = 0.5 / `sateffect'
di `satdiff'


*************************
********* Part 2 ********
*************************

********************************
********* 2.a. to 2.d **********

generate female_black = female * black
browse female black female_black

regress sat hsize hsizesq female black female_black

* How to interpret the effect of high school size:
sum hsize, det

preserve 
keep if _n <= 20
gen hsizeeffect = (_n/2) * _b[hsize] + (_n/2)^2 * _b[hsizesq]
gen hstudents = 100* _n/2
line hsizeeffect hstudents
restore

preserve 
keep if _n <= 20
gen hsizemarginaleffect = _b[hsize] + 2 * (_n/2) * _b[hsizesq]
gen hstudents = 100* _n/2
line hsizemarginaleffect hstudents
restore

* The interpretation of coefficient on dummies and interactions can be more easily grasped through the following example:
regress sat female black female_black
summarize sat if female==0 & black==0
summarize sat if female==0 & black==1
summarize sat if female==1 & black==0
summarize sat if female==1 & black==1


************************
********* 2.e **********

generate male = (female==0)
browse male female
generate male_black = male * black

regress sat hsize hsizesq male black male_black

* Again, the interpretation of coefficient on dummies and interactions can be more easily grasped through the following example:
regress sat male black male_black
summarize sat if female==0 & black==0
summarize sat if female==0 & black==1
summarize sat if female==1 & black==0
summarize sat if female==1 & black==1



*************************
********* Part 3 ********
*************************

************************
********* 3.b **********

regress colgpa hsize hsizesq hsperc sat female athlete


************************
********* 3.c **********

regress colgpa hsize hsizesq hsperc female athlete


************************
********* 3.d **********

gen female_athlete = female * athlete 

regress colgpa hsize hsizesq hsperc sat female athlete female_athlete


************************
********* 3.e **********

gen female_sat = female * sat 

regress colgpa hsize hsizesq hsperc athlete sat female female_sat


log close

