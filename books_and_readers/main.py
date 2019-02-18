import psycopg2
import boto3
import argparse
import logging
from logging.handlers import RotatingFileHandler

from books_and_readers.summary_tables_queries import *


def parse_args():
    parser = argparse.ArgumentParser(description='This scripts pushes BR tables from RDS to Redshift')
    parser.add_argument('selected_date', help='date of the data that we want to push')
    args = parser.parse_args()
    return args


class BRDatabase:
    """
    This class initiates a connection and a cursor on a PostgreSQL database and defines a few actions to help
    manipulating the database
    """
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        try:
            self.conn = psycopg2.connect(host=host, database=database, port=port, user=user, password=password)
            self.cur = self.conn.cursor()

            logging.info(self.conn.get_dsn_parameters())
            self.cur.execute("SELECT version();")
            record = self.cur.fetchone()
            logging.info("You are connected to - {}".format(record))

        except (Exception, psycopg2.Error) as error:
            logging.error("Error while connecting to PostgreSQL", error)

    def select_query(self, query):
        self.cur.execute(query)
        rows = self.cur.fetchall()
        for row in rows:
            return row[0]

    def empty_table(self, table):
        self.cur.execute("delete from {}".format(table))
        self.conn.commit()

    def copy_command(self, bucket, table, scheduled_date, time_field, role):
        if self.select_query("SELECT COUNT(*) FROM {0} WHERE {2}::varchar LIKE '{1}%'".format(
                table, scheduled_date, time_field)) == 0:
            self.cur.execute(
                "copy {1} from 's3://{0}/dumps/{2}/{1}.csv' iam_role '{3}' csv".format(
                    bucket, table, scheduled_date.replace('-', '/'), role))
            self.conn.commit()
        else:
            logging.warning('Data already exists in the table {0} for date {1}. Copy skipped.'.format(
                table, scheduled_date))

    def copy_table_to_local_file(self, table, path, scheduled_date, time_field):
        with open(path, 'w') as f:
            self.cur.copy_expert("copy (SELECT * FROM {0} WHERE {1}::varchar LIKE '{2}%') to stdout csv".format(
                table, scheduled_date, time_field), f)
            self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()


def push_csv_to_s3(table, directory, bucket, scheduled_date):
    """
    This function pushes a local csv file into a timestamped S3 object
    """
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file('{0}/{1}.csv'.format(directory, table),
                               bucket,
                               'dumps/{0}/{1}.csv'.format(scheduled_date.replace('-', '/'), table))


def main():

    br_logger = logging.getLogger()
    br_logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-9s %(message)s')
    file_handler = RotatingFileHandler('br_pipeline.log', 'a', 100000, 1)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    br_logger.addHandler(file_handler)

    selected_date = parse_args().selected_date
    base_dir = '/home/julaff/PycharmProjects/books_and_readers'
    s3_bucket = 'julaff-books-and-readers-exercise'
    redshift_role = '###'

    db_rds = BRDatabase('###.eu-west-1.rds.amazonaws.com',
                        5432,
                        '###',
                        '###',
                        '###')

    db_rds.copy_table_to_local_file('book', '{}/book.csv'.format(base_dir), 'createtime', selected_date)
    db_rds.copy_table_to_local_file('br_user', '{}/br_user.csv'.format(base_dir), 'createdat', selected_date)
    db_rds.copy_table_to_local_file('log', '{}/log.csv'.format(base_dir), 'created_at', selected_date)
    db_rds.close()

    push_csv_to_s3('book', base_dir, s3_bucket, selected_date)
    push_csv_to_s3('br_user', base_dir, s3_bucket, selected_date)
    push_csv_to_s3('log', base_dir, s3_bucket, selected_date)

    db_redshift = BRDatabase('###.eu-west-3.redshift.amazonaws.com',
                             5439,
                             '###',
                             '###',
                             '###')

    db_redshift.copy_command(s3_bucket, 'book', selected_date, 'createtime', redshift_role)
    db_redshift.copy_command(s3_bucket, 'br_user', selected_date, 'createdat', redshift_role)
    db_redshift.copy_command(s3_bucket, 'log', selected_date, 'created_at', redshift_role)

    db_redshift.empty_table('reading_by_country')
    db_redshift.empty_table('reading_by_language')
    db_redshift.empty_table('reading_by_gender')
    db_redshift.empty_table('search_summary')

    db_redshift.cur.execute(reading_by_country_query)
    db_redshift.cur.execute(reading_by_language_query)
    db_redshift.cur.execute(reading_by_gender_query)
    db_redshift.cur.execute(search_summary_query)

    db_redshift.conn.commit()
    db_redshift.close()


if __name__ == '__main__':
    main()
