messages = {}

TODAY = "12 December 2023 "


messages['DS - computing tier NE_to_SETU rates'] = f"""\
_Of the domestic, 23 and under, full-time New Entrants, what rate enroll in SETU?_

Data taken from [hea.ie](https://hea.ie/statistics/data-for-download-and-visualisations/access-our-data/access-our-data-students/) 
under report heading `Students/Geographical Breakdown` with options
  * `Age Group` = `23_and_under`
  * `Course Level` = `Undergraduate`
  * `Gender` = `All`
  * `Institute` = `All` or `SETU Carlow` or `SETU Waterford` or (`SETU Carlow` and `SETU Waterford`)
  * `New Entrant?` = `Yes`
  * `Programme Type` = `All`
  * `Mode of Study` = `Full-time`

As of {TODAY}, the data covers 2016/17 to 2022/23.  
"""

messages['computing tier NE_to_SETU rates'] = f"""\
The New Entrant to SETU rate for each tier for each year, are calculated by grouping the New Entrants by tier and year,
then dividing the number of New Entrants enrolling at SETU by the number of New Entrant going to all institutions.

"""

messages['Tier NE_to_SETU rates'] = f"""\
The following graph and table 
"""

messages['DS - computing tier NE proportions'] = f"""\
_Of the domestic, 23 and under, full-time New Entrants, what proportion are from each tier?_

Using the same data as for the New Entrant to SETU rates, group New Entrants by tier and sum.
"""


messages['DS - LC Enrolment by tier'] = f"""\
_Of the LC2 enrolments, what proportion are from each tier?_

  Data taken from [gov.ie / DoE / Post-primary schools enrolment figures](https://www.gov.ie/ga/bailiuchan/post-primary-schools/)

Report: Post-primary schools 2020/2021, 2021/2022, 2022/2023
  * Prior to 2020/2021 the dataset did not breakdown by year 
  * In 2020/2021 there was no `County` field => computed one based on `Local Authority`
"""


messages['DS - LC Enrolment (Projection)'] = f"""\

_How many LC2 enrolments are expected national over 2021-2040?_

Data taken from [gov.ie / DoE / Projections](https://www.gov.ie/en/collection/projections/?referrer=http://www.education.ie/en/Publications/Statistics/projections/#)

Report and XLSX: Projections of full-time enrolment Primary and Second Level 2021 - 2040
"""


messages['DS - Transfer rate from second to third level - 1'] = f"""\

_What proportion of LC2 enrollments transfer to third level HEI?_

Data taken from [gov.ie / DoE / Projections](https://www.gov.ie/en/collection/projections/?referrer=http://www.education.ie/en/Publications/Statistics/projections/#)

Report and XLSX: Projections of demand for full time Third Level Education 2021-2040

The above report lists transfer rates based on matching students using their PPSN from 
2nd level to 3rd level. The resulting overall transfer rates and the component lags are:
"""

messages['DS - Transfer rate from second to third level - 2'] = f"""\
A less rigorous approach, but one that allows tier-specific transfer rates is to compare   
the New Entrant data from the HEA and
the LC2 enrolments from the post-primary schools enrolment figures for the previous academic year.
"""


messages['DS - Rate of Undergraduate Turnover (ROUT) - 1'] = """\

_Of the current national, undergraduate full-time students, what proportion will be enrolled in the following academic year?_ 

The approach here follows the procedure in the DoE's 3rd level projections report:
$$ 
\\mathrm{ROUT} = \\frac{\\mathrm{Stock}_{t+1} - \\mathrm{Entrants}_{t+1} } {\\mathrm{Stock}_{t} }
$$
where 

 * $\\mathrm{Stock}_{t+1}$ is total national students enrolment in full-time undergraduate courses in year $t$.
 * $\\mathrm{Entrants}_{t+1}$ total intake to full-time, national students undergraduate courses in year $t+1$.

However given the university's SRS returns a more rigorous approach is possible &mdash; using 
student identification numbers. We should consider this.

"""