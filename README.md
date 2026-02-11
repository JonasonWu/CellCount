# Instructions
## Method 1: Using Python Application
* Double click on the python application to run.
* Run applications in the following order:
    * load_data.py
    * initial_analysis.py
    * statistical_analysis.py
    * subset_analysis.py

## Method 2: Using Terminal
* Open the terminal.
* Navigate to the directory of this project.
* Run python scripts in following order:
    * python load_data.py
    * python initial_analysis.py
    * python statistical_analysis.py
    * python subset_analysis.py

# Files
## load_data.py
* Uses the data from the cell-count.csv and creates the cell_counts.db database.
## initial_analysis.py
* Answers the question: What is the frequency of each cell type in each sample?
* Displays a summary table of the relative frequency of each cell population into relative_frequency.txt.
## statistical_analysis.py
* Not completed.
## subset_analysis.py
* Performs an analysis of PBMC samples at baseline. Prints out the results on the terminal.

# Database Design
* The CSV has unique identifiers already, and SQLite doesn't seem to support uuid well, so it's better to just define the colums that can serve as primary keys.
* The data was loaded into 3 tables: projects, subjects, samples.
    * projects
        * This table only has project_id, which is the primary key, collected as the project column in the csv.
        * This table would be useful to keep, in the case where we want to create a new project that doesn't have any subjects at the moment.
        * This table would be open to extension, allowing project descriptions to be added if desired.
    * subjects
        * This table records every subject that is part of all clinical trials.
        * The primary key would be the subject column of the csv.
        * Each row should represent a subject that has a particular condition, enclosed within the specific clinical trial.
        * Defines unique attributes of the subject, like condition, age, sex, treatment, response, and project_id. We assume that these attributes will not change throughout the clinial trials.
        * Note: In the future, if the same subject comes back to participate in some other project, we should reidentify them with another subject_id, because all of those attributes will most likely have changed.
        * The treatment column is indexed to allow faster filtering for SQL statements. There aren't many treatment options at the moment, but new treatment options may be added in the future, so I choose to index them now.
        * Note that columns like sex and response are not worth indexing because they only have few possible values.
    * samples
        * This table records every sample collected from subjects.
        * Each row should represent a sample collected from a subject.
        * Defines all specific attributes relating to the sample, like sample_type, time_from_treatment_start, cell counts, and subject_id.
        * Note: Even though it seems that sample_type is the same based on the project, but I still believe it's best to include sample_type in the samples table. sample_type should be specific to the sample, not the project. There is no rule stating that a single project should only take in one type of sample.
        * The time_from_treatment_start column is indexed to allow for future expansion. Maybe future projects may use other time intervals for the project, so indexing would be helpful.
        