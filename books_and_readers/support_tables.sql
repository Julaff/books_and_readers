DELETE FROM countries;
copy countries from 's3://julaff-books-and-readers-exercise/data_csv.csv' iam_role '###' csv ignoreheader 1;

DELETE FROM languages;
copy languages from 's3://julaff-books-and-readers-exercise/iso-639-3_Name_Index.tab' iam_role '###' delimiter '\t' ignoreheader 1;

DELETE FROM gender;
INSERT INTO gender VALUES
    (0, 'unknown'),
    (1, 'female'),
    (2, 'male')
;
