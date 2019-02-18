reading_by_country_query = """INSERT INTO reading_by_country
                              SELECT countries.name AS country_name, title, COUNT(DISTINCT log.client_id) as readers_in_country
                              FROM log
                              JOIN book ON log.book_id=book.uuid
                              JOIN countries ON log.country=countries.code
                              WHERE url LIKE '/Book/Read/%page%'
                              GROUP BY countries.name, title
                              ;"""

reading_by_language_query = """INSERT INTO reading_by_language
                               SELECT languages.name AS language_name, COUNT(DISTINCT TITLE) AS books_read, COUNT(title) AS pages_read
                               FROM log
                               JOIN book ON log.book_id=book.uuid
                               JOIN languages ON book.language=languages.code
                               WHERE url LIKE '/Book/Read/%page%'
                               GROUP BY languages.name
                               ;"""

reading_by_gender_query = """INSERT INTO reading_by_gender
                             SELECT gender.name AS gender_name, COUNT(DISTINCT TITLE) AS books_read, COUNT(title) AS pages_read, cast(pages_read as decimal) / books_read as pages_per_book
                             FROM log
                             JOIN book ON log.book_id=book.uuid
                             JOIN br_user ON log.user_id=br_user.id
                             JOIN gender ON br_user.usergender=gender.code
                             WHERE url LIKE '/Book/Read/%page%'
                             GROUP BY gender.name
                             ;"""

search_summary_query = """INSERT INTO search_summary
                          SELECT REGEXP_REPLACE(url, '^.*Query=|&.*$') AS term, COUNT(term) as number_of_searches
                          FROM log
                          WHERE url LIKE '/Search/Results?Query=%'
                          GROUP BY term
                          ;"""
