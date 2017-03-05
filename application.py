from flask import Flask

app = Flask(__name__)


@app.route('/')
def main():
    # Uploading data
    # step 0, Create s3 private bucket
    #
    # step 1, copy data to s3 private bucket
    #
    # step 2, parse data, skip re-download since we know we're not changing private bucket data
    # outside of this program
    #
    # step 3, populate table from input file


    pass


if __name__ == '__main__':
    app.run()
