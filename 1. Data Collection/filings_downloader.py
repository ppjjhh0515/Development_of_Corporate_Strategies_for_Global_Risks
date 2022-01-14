from sec_edgar_downloader import Downloader
import pandas as pd
import time
import sys
import argparse

# install the dependency of sec-edgar-downloader
# pip install -U pip install sec-edgar-downloader

def filter_ciks(sectors, sub_paths=["2019q1", "2019q2", "2019q3", "2019q4", "2020q1", "2020q2", "2020q3", "2020q4", "2021q1"]):
    """
    Extract all ciks according to sector code (sic), for example,  manufacturing has sic code from 2000 to 2999
    reference: https://en.wikipedia.org/wiki/Standard_Industrial_Classification
    """
    results = set()
    for path in sub_paths:
        df = pd.read_csv(path + "/sub.txt", sep="\t", low_memory=False)
        for start, end in sectors:
            results.update(df[(start <= df.sic) & (df.sic <= end)].cik)
    return list(results)



def download_filings(ciks, doc_type, amount, retry, target_folder, start, end):
    """
    Download fillings according to desired document type and amount of docs

    ciks: list of int, list of cik

    doc_type, amount, retry, target_folder, start, end: the same as parameters in main
    """

    # initialize Downloader, save files in target folder
    dl = Downloader(target_folder)

    # extract subset of ciks, default subset equals to the original one
    ciks = ciks[start:end]

    # iterate ciks, download files for each cik
    for idx, cik in enumerate(ciks):
        # cik is a ten digits string, original cik ignores the leading zeros
        cik = '%010d' % cik

        # while loop for retry, if error occurs and retry is set to true, the loop will not be broken until
        # downloading file succeed; if downloading file succeed, break while loop
        while(True):
            try:
                # download file, based on doc_type, cik and amount
                number = dl.get(doc_type, cik, amount=amount)
                print(f"CIK: {cik} - {idx + 1}/{len(ciks)} ({number} files has been downloaded)...")
                break
            except Exception as e:
                print(e)
                if not retry:
                    break

                # sleep 1 second in case of the error related to too frequent
                # retriving files using the same IP
                time.sleep(1)


def main(target_sectors, doc_type, amount, retry, target_folder, start, end):
    """
    main function to download filings of given doc_type to target_folder

    target_sectors: list of tuple, each tuple has 2 elements, represent the start sic and end sic of that sector.

    doc_type: str, the filings type, 10-K, 10-Q, 8-K, etc.

    amount: int, how many files to download, from latest to oldest.

    retry: bool, whether to retry download when error occurs

    target_folder: str, the path to save download files

    start: int, start index of ciks (in case that we stop downloading, having this parameter, we could resume program at given point)

    end: int, end index of ciks (like start)
    """

    # filter out desired ciks (ciks from given sectors)
    ciks = filter_ciks(target_sectors)

    # download filings of give type, default is 10-K
    download_filings(ciks, doc_type=doc_type, amount=amount, retry=retry, 
        target_folder=target_folder, start=start, end=end)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Configuration of downloader')
    parser.add_argument('--doc_type', metavar='DT', nargs='?', type=str, default='10-K', help='document type 10-K, 10-Q and so on')
    parser.add_argument('--amount', metavar='A', nargs='?', type=int, default=3, help='number of documents to download')
    parser.add_argument('--retry', metavar="R", nargs='?', type=bool, default=False, help='whether to retry fetch doc when error occurs')
    parser.add_argument('--dest', metavar="D", nargs='?', type=str, default="./", help='whether to retry fetch doc when error occurs')
    parser.add_argument('--start', metavar="S", nargs='?', type=int, default=0, help="start index of ciks")
    parser.add_argument('--end', metavar="E", nargs='?', type=int, default=-1, help="end index of ciks")

    args = parser.parse_args()
    
    target_sectors = [(2000, 3999), (7000, 8999)]
    main(target_sectors, args.doc_type, args.amount, args.retry, args.dest, args.start, args.end)



