# Module 2 Homework

ATTENTION: At the end of the submission form, you will be required to include a link to your GitHub repository or other public code-hosting site. This repository should contain your code for solving the homework. If your solution includes code that is not in file format, please include these directly in the README file of your repository.

> In case you don't get one option exactly, select the closest one

For the homework, we'll be working with the _green_ taxi dataset located here:

`https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/green/download`

To get a `wget`-able link, use this prefix (note that the link itself gives 404):

`https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/`

### Assignment
So far in the course, we processed data for the year 2019 and 2020. Your task is to extend the existing flows to include data for the year 2021.

![homework datasets](../../../02-workflow-orchestration/images/homework.png)

As a hint, Kestra makes that process really easy:
1. You can leverage the backfill functionality in the scheduled flow `09_gcp_taxi_scheduled.yaml` to backfill the data for the year 2021. Just make sure to select the time period for which data exists i.e. from `2021-01-01` to `2021-07-31`. Also, make sure to do the same for both `yellow` and `green` taxi data (select the right service in the `taxi` input).
2. Alternatively, run the flow manually for each of the seven months of 2021 for both `yellow` and `green` taxi data. Challenge for you: find out how to loop over the combination of Year-Month and `taxi`-type using `ForEach` task which triggers the flow for each combination using a `Subflow` task.


> [!TIP] 
> **My Answer:**
> Flow `04` required manual change to add the year 2021 as one of the possible variables for the input "year".
> Flow `08` has fixed years 2019 and 2020, but also `allowCustomValue` is set to `true`, so it is not strictly required.
> The other flows handle different years well, using `trigger.date`.

### Quiz Questions
Complete the quiz shown below. It's a set of 6 multiple-choice questions to test your understanding of workflow orchestration, Kestra, and ETL pipelines.

> [!TIP] 
> **My Answer:**
> For the following questions I only need the entire year 2020 (Q1-Q4). For the assignment and Q5 I need the entire 2021 (available from 2021-01-01 to 2021-07-31).
> For convenience, I'm going to skip 2019, and will only backfill the entire 2020 and 2021. 
> 
> I run the full backfill (years: 2020 and 2021) at this point. 
> I run the flow `09_gcp_taxi_scheduled.yaml` with the backfilling options, with the dates set for: 
> - 2020: start_date: 2020-01-01 00:00:00; end_date: 2021-01-01 00:00:00
> - 2021: start_date: 2021-01-01 00:00:00; end_date: 2021-08-01 00:00:00

1) Within the execution for `Yellow` Taxi data for the year `2020` and month `12`: what is the uncompressed file size (i.e. the output file `yellow_tripdata_2020-12.csv` of the `extract` task)?
- 128.3 MiB
- 134.5 MiB
- 364.7 MiB
- 692.6 MiB

> [!TIP] 
> **My Answer:**
> I found this information in Executions --> file:yellow_tripdata_2020-12.csv --> METRICS --> file_size = 134,481,400 bytes = 128.26 MiB
>
> ![Q1 Answer](module02_Q1.png)

2) What is the rendered value of the variable `file` when the inputs `taxi` is set to `green`, `year` is set to `2020`, and `month` is set to `04` during execution?
- `{{inputs.taxi}}_tripdata_{{inputs.year}}-{{inputs.month}}.csv` 
- `green_tripdata_2020-04.csv`
- `green_tripdata_04_2020.csv`
- `green_tripdata_2020.csv`

> [!TIP] 
> **My Answer:** `green_tripdata_2020-04.csv`

3) How many rows are there for the `Yellow` Taxi data for all CSV files in the year 2020?
- 13,537.299
- 24,648,499
- 18,324,219
- 29,430,127

> [!TIP] 
> **My Answer:** I answered this in GCP, using BigQuery. The answer is **24,648,499**
>
> ```sql
> SELECT COUNT(*)
> FROM `sacred-result-486116-e1.zoomcamp.yellow_tripdata`
> WHERE filename LIKE '%2020%';
> ```
>
> ![Q3 Answer](module02_Q3.png)

4) How many rows are there for the `Green` Taxi data for all CSV files in the year 2020?
- 5,327,301
- 936,199
- 1,734,051
- 1,342,034

> [!TIP] 
> **My Answer:** I answered this in GCP, using BigQuery as in Q3 but specifying now the green taxis data. The answer is **1,734,051**
>
> ```sql
> SELECT COUNT(*)
> FROM `sacred-result-486116-e1.zoomcamp.green_tripdata`
> WHERE filename LIKE '%2020%';
> ```

5) How many rows are there for the `Yellow` Taxi data for the March 2021 CSV file?
- 1,428,092
- 706,911
- 1,925,152
- 2,561,031

> [!TIP] 
> **My Answer:** The correct answer is **1,925,152**.
>
> ```sql
> SELECT COUNT(*)
> FROM `sacred-result-486116-e1.zoomcamp.yellow_tripdata`
> WHERE filename LIKE '%2021-03%';
> ```

6) How would you configure the timezone to New York in a Schedule trigger?
- Add a `timezone` property set to `EST` in the `Schedule` trigger configuration  
- Add a `timezone` property set to `America/New_York` in the `Schedule` trigger configuration
- Add a `timezone` property set to `UTC-5` in the `Schedule` trigger configuration
- Add a `location` property set to `New_York` in the `Schedule` trigger configuration

> [!TIP] 
> **My Answer:** Add a `timezone` property set to `America/New_York` in the `Schedule` trigger configuration

