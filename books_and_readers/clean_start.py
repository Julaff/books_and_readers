from books_and_readers.main import BRDatabase

if __name__ == '__main__':

    db_redshift = BRDatabase('julaff-redshift-br-exercise.cyzueu55bhgp.eu-west-3.redshift.amazonaws.com',
                             5439,
                             'brtest',
                             'julien',
                             '###')

    db_redshift.empty_table('book')
    db_redshift.empty_table('br_user')
    db_redshift.empty_table('log')

    db_redshift.cur.execute(
        "copy book from 's3://julaff-books-and-readers-exercise/raw/book.csv' iam_role '###' csv")
    db_redshift.cur.execute(
        "copy br_user from 's3://julaff-books-and-readers-exercise/raw/br_user.csv' iam_role '###' csv")

    db_redshift.cur.execute("delete from book where createtime::varchar LIKE '2017-01-28%'")
    db_redshift.cur.execute("delete from book where createtime::varchar LIKE '2017-01-29%'")
    db_redshift.cur.execute("delete from book where createtime::varchar LIKE '2017-01-30%'")
    db_redshift.cur.execute("delete from br_user where createdat::varchar LIKE '2017-01-28%'")
    db_redshift.cur.execute("delete from br_user where createdat::varchar LIKE '2017-01-29%'")
    db_redshift.cur.execute("delete from br_user where createdat::varchar LIKE '2017-01-30%'")

    db_redshift.conn.commit()
    db_redshift.close()
