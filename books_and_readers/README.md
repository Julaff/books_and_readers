
# Books and Readers Technical Exercise  - J. Laffargue
  
The following document will present my step-by-step approach into solving the provided exercise.  

# Table of Contents
1. [Prerequisites](#prerequisites)
2. [Data Description](#data-description)
3. [Creating a Data warehouse](#creating-a-data-warehouse)
4. [Creating empty tables](#creating-empty-tables)
5. [Manually inserting data to format tables](#manually-inserting-data-to-format-tables)
6. [Building the pipeline](#building-the-pipeline)
7. [Building and Querying Summary tables](#building-and-querying-summary-tables)
8. [Scheduling the ETL](#scheduling-the-etl)
9. [Analysis](#analysis)



## 1. Prerequisites  
  
To do the exercise I used :  
  
* A connection to Amazon RDS, to get the incoming data  
* An Amazon Redshift cluster, to be used as a data warehouse  
* Amazon S3 to backup the data, and to transfer to Redshift  
* Python 3.7 with libraries psycopg2 and boto3, to interact with the 3 services above  

The attached files must all belong in the same folder.
  
## 2. Data Description  
  
The 3 required RDS tables are already summarized in the instructions, but we can consider the whole as a simple star schema, with the `log` table being the fact table, and the `book` and `br_user` tables being dimension tables.    
  
3 support tables will also be created in the Redshift cluster, as required, in order to write clearly the genders, countries, and languages.    
  
Summary tables will also be created.  

## 3. Creating a Data warehouse
I've chosen to create a small Redshift cluster.  

The JDBC url is : (cluster deleted)  

Also, I've created an S3 bucket : `julaff-books-and-readers-exercise` from which the data will be sent to Redshift.  

## 4. Creating empty tables
### Reproducing RDS tables
The DDL for tables `book`, `br_user`, and `log` is already provided.  
I had to add an additional bigint field in the `book` table.

### Format tables and summary tables
Format tables to be created : `countries`, `languages`, `gender`  
Summary_tables to be created : `reading_by_country`, `reading_by_language`, `reading_by_gender`, `search_summary`  
The declaration is straight-forward, and included in the attached file `ddl.sql`
  
## 5. Manually inserting data to format tables
Format tables respond to fixed rules and will not be updated in the ETL process.  
For the `gender` table, consisting of 3 lines, I've chosen to do a manual INSERT command.  
For the `countries` and `languages` table, they each follow an ISO norm, so I got the data online from the links below :  
For `countries` : https://iso639-3.sil.org/sites/iso639-3/files/downloads/iso-639-3_Name_Index.tab
For `languages` : https://datahub.io/core/country-list/r/data.csv

These 2 datasets were then uploaded with a COPY command, see attached file `support_tables.sql`.

## 6. Building the pipeline
The chosen approach is a Dump and Load approach. The reasons are :
* The data size is big but reasonable
* AWS Data Pipeline could work but is less transparent.
* Using Kinesis Stream/Firehose could work as well, but is not designed for doing daily batch.
 
The main inconvenient is the temporary dump on the local machine, but to my knowledge, only Aurora gives the possibility to transfer directly from RDS to S3. Of course, adding an EC2 server would be more secured regarding data, but to complete this exercise I chose to do without, for practical reasons.

The steps to the pipeline consist of :
1. Exporting the data, fragmented by day, from the 3 tables of the RDS Database to local csv files.
2. Pushing the 3 csv files corresponding to the desired date to dated S3 objects.
3. Pushing the data to the 3 equivalent Redshift tables, after making sure that it is not already there.
4. Updating the summary tables

Python has libraries that interact very well with S3 and PostgreSQL, both on RDS and Redshift.  
The python code is available in the attached `main.py` file and requires one parameter, the day from which we want extract transform and load data (for example 2017-01-28).  

I also quickly made a `clean_start.py` file, specific of this exercise, that makes sure that the `book` and `br_user` tables already have data, excluding the 3 days we want to insert.

### Remarks
I didn't add any `VACUUM ANALYZE` in the ETL as it is often dependent to the time of the schedule. However, the command should be done regularly.

## 7. Building and Querying Summary tables
### Assumptions
Beforehand, we will make some assumptions :    
  
We will suppose that a log line corresponding to reading is a log line identifying a page in a book,   
which we will identify with the clause `WHERE url LIKE '/Book/Read/%page%'`  
  
Next, let's execute the following query :  
```  
SELECT client_id, count(*)  
FROM log  
WHERE url LIKE '/Book/Read/%page%'  
GROUP BY client_id  
ORDER BY count desc  
LIMIT 10  
;  
```  
The result shows that most of the readers don't have a user_id, which, I suppose, means that they are not registered, and registered readers are not representative of all readers.  
  
Now, let's replace user_id with client_id:  
```  
SELECT client_id, count(*)  
FROM log  
WHERE url LIKE '/Book/Read/%page%'  
GROUP BY client_id  
ORDER BY count desc  
LIMIT 10  
;  
```  
The result show that every page read corresponds to a client ID.    
For the following, we will make the **strong assumption** that every client ID corresponds to a unique reader, meaning that every reader reads on one device only.  

### TOP-20 for each required query
The declaration of each query is in `summary_tables.sql`

### reading_by_country
Output of the following query :
```
SELECT * FROM reading_by_country
ORDER BY readers_in_country DESC, country_name, title
LIMIT 20;
```

|country_name|title|readers_in_country|
|--|--|--|
|Nigeria|Broken Promises|3930|
|Nigeria|Sugar Daddy|3792|
|South Africa|First Love… Thinking of Him|2724||
|South Africa|Broken Promises|2415|
|Nigeria|Siren’s Treasure|1719|
|South Africa|Sugar Daddy|1681|
|Philippines|Ang Pakikipagsapalaran ng mga Bayani (Unang libro sa Singsing ng Salamangkero)|1594|
|South Africa|There's Something about Him|1170|
|Côte d'Ivoire|Le Roman de la momie|1139|
|Philippines|First Love… Thinking of Him|926|
|Uganda|Forever My Love|868|
|South Africa|Forbidden Love|854|
|Philippines|Sex, Not Love (The Break Up)|826|
|South Africa|Damaged Souls|813|
|Philippines|The Girl with the Magic Hands|777|
|South Africa|Scars of Love|767|
|Zambia|Forever My Love|726|
|Nigeria|Forbidden Love|702|
|South Africa|Siren’s Treasure|686|
|Kenya|Forever My Love|649|

### reading_by_language
Output of the following query :
```
SELECT * FROM reading_by_language
ORDER BY pages_read DESC, books_read DESC, language_name
LIMIT 20;
```
|language_name|books_read|pages_read|
|--|--|--|
|English|5889|688298|
|French|491|47751|
|Spanish|235|23085|
|Arabic|180|13248|
|Tagalog|1|4633|
|Portuguese|113|4087|
|Swahili (macrolanguage)|79|295|
|Hausa|19|280|
|Urdu|13|183|
|Afrikaans|33|160|
|Xhosa|38|153|
|Thai|3|70|
|Hindi|5|48|
|Indonesian|2|30|
|Ganda|8|28|
|Akan|2|23|
|Gujarati|2|23|
|Sepedi|11|19|
|Tswana|8|17|
|Adamawa Fulfulde|1|13|

![Bar chart](https://s3.eu-west-3.amazonaws.com/julaff-books-and-readers-exercise/IMG/br_barchart.png)  
Representation of the above data with Bar charts. It illustrates well that English is by far the most read language

### reading_by_gender
```
SELECT * FROM reading_by_gender
ORDER BY pages_read DESC, books_read DESC, gender_name;
```
|gender_name|books_read|pages_read|pages_per_book|
|--|--|--|--|
|unknown |1175|19063|16.22|
|female  |729|11490|15.76|
|male    |829|9453|11.40|

![Pie chart](https://s3.eu-west-3.amazonaws.com/julaff-books-and-readers-exercise/IMG/br_pie.png)  
Representation of the above data with Pie charts

### search_summary
```
SELECT * FROM search_summary
ORDER BY number_of_searches DESC
LIMIT 20;
```
|term|number_of_searches|
|--|--|
|%22picture+of+dorian%22|4320|
|sex|286|
|Sex|146|
|love|139|
|wattpad|108|
|bible|79|
|Bible|65|
|Wattpad|59|
|things+fall+apart|51|
|animal+farm|51|
|fifty+shades+of+grey|50|
|harry+potter|50|
|sex+story|49|
|Love|47|
|porno|47|
|biology|45|
|horror|45|
|tagalog|43|
|vampire|42|
|love+story|41|

![Wordcloud](https://s3.eu-west-3.amazonaws.com/julaff-books-and-readers-exercise/IMG/br_wordcloud.png)  
Representation as a wordcloud, with the first occurence removed.
  
## 8. Scheduling the ETL
It's a simple Python program with one date parameter, so to schedule it I would simple do it with crontab. So for example, if I want to execute it in the morning, 3 times, corresponding to the 3 days of data, I would do something like :
```
00 06 * * * /my/package/dir/br_main.py 2017-01-28
05 06 * * * /my/package/dir/br_main.py 2017-01-29
10 06 * * * /my/package/dir/br_main.py 2017-01-30
```

## 9. Analysis  
  
### Things I've noticed
* Africa is the mostly represented continent
* Female readers have a significantly bigger pages-per-book ratio than male readers whereas male readers read more books
* English is by far the most read language
* The search for "the portrait of dorian" is surprisingly high and above all other search terms
* Tagalog is one of the most read languages, but only in a single book. It's also a term searched a lot.

### Things to explore
* It would be interesting to explain the difference of pages-per-book ratios between male and female readers. For example, do male readers read shorter books, or do they tend to switch book without finishing the current one ?
* The RDS database has a `category` table that isn't mentioned in the exercise. It would be interesting to add it to the pipeline and make analysis with it. For example, the favorite categories by gender, or by continent.
* The demand for tagalog language seems very big compared to the choice of books in that language. The data seems to indicate that getting more books in that language would be beneficial to the readers.

### Additional queries to consider
* Following the same idea than the issue with the tagalog language, it could interesting to put side to side the ratio of available books per language with the ratio of books actually read per language. It would help understanding as well if the high number of books read in English is a consequence of availability or of real demand.
* Worldwide, the male/female ratio is pretty well balanced. It could be interesting to see if it's still the case locally.
* With a similar objective, the variable age hasn't been used at all. The amount of reading per age could be a good indicator of which books to offer in the future.

### Time spent reading by users
The first approach to see the time spent reading by user is to order on the `url` field from the `log` table, for every log that indicates a page from a book. This way, the succession of pages read is listed by user.  
The time gap between each successive `created_at` field will represent the time spent by page, as the end time of reading page N usually corresponds of the begin time of reading page N+1.  
However, this approach is too basic to be really efficient : some people like to browse pages quickly before deciding if they're going to start reading a book; some other people keep going back a few pages to review a point they miss; and most people, as said in the question, also take breaks from time to time. The `pageSize` criteria has also a direct impact on the time spent reading per page.  
For this last point, creating a field that does a ratio between time spent and pageSize should be the most useful thing to do.  
For the other issues, I suppose that it's mostly a Machine Learning question. Collaborative filtering would probably allow to regroup these various behaviors into a finite number of meaningful clusters, as well as identifying outliers. For this to work, we would probably need to work on a period longer than the 3 days provided, as the reading habits of people vary depending of the day.
