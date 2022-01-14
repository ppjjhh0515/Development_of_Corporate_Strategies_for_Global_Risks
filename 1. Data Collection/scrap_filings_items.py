from bs4 import BeautifulSoup
import os
import re
import pandas as pd

def find_filings_paths(doc_type="10-K",base_path='./data/',year="19"):
    base_path = os.path.join(base_path,doc_type)
    list_10K_paths = []
    file_path = os.path.join(base_path,year)
    ciks = os.listdir(file_path)
    for cik in ciks:
        if cik == ".DS_Store":
            continue
        cik_file_path = os.path.join(file_path,cik)
        submission_paths = os.listdir(cik_file_path)
        for submission_path in submission_paths:
            if submission_path == ".DS_Store":
                continue
            detail_path = os.path.join(cik_file_path, submission_path, "filing-details.html")
            list_10K_paths.append(detail_path)
    return list_10K_paths

def generate_key(section, next_section):
    return section + " to " + next_section

class TenKScraper:
    def __init__(self, section, next_section):
        self.all_section = [str(i) for i in range(1, 16)] + ['1A', '1B', '7A', '9A', '9B']
        section = re.findall(r'\d.*\w*', section.upper())[0]
        next_section = re.findall(r'\d.*\w*', next_section.upper())[0]
        if section  not in self.all_section:
            raise ValueError(f'Section: {section} is not avaiable, avaiable section: {self.all_section}')
        if next_section  not in self.all_section:
            raise ValueError(f'Section: {next_section} is not avaiable, avaiable section: {self.all_section}')
        self.section = 'Item ' + section
        self.next_section = 'Item ' + next_section
            



    def scrape(self, input_path):
        with open(input_path, 'rb') as input_file:
            page = input_file.read()  # <===Read the HTML file into Python
            # Pre-processing the html content by removing extra white space and combining then into one line.
            page = page.strip()  # <=== remove white space at the beginning and end
            page = page.replace(b'\n', b' ')  # <===replace the \n (new line) character with space
            page = page.replace(b'\r', b'')  # <===replace the \r (carriage returns -if you're on windows) with space
            page = page.replace(b'&nbsp;',
                                b' ')  # <===replace "&nbsp;" (a special character for space in HTML) with space.
            page = page.replace(b'&#160;',
                                b' ')  # <===replace "&#160;" (a special character for space in HTML) with space.

            while b'  ' in page:
                page = page.replace(b'  ', b' ')  # <===remove extra space

            # Using regular expression to extract texts that match a pattern

            # Define pattern for regular expression.
            # The following patterns find ITEM 1 and ITEM 1A as diplayed as subtitles
            # (.+?) represents everything between the two subtitles
            # If you want to extract something else, here is what you should change

            # Define a list of potential patterns to find ITEM 1 and ITEM 1A as subtitles
            p1 = bytes(r'bold;\">\s*' + self.section + r'\.(.+?)bold;\">\s*' + self.next_section + r'\.',
                       encoding='utf-8')
            p2 = bytes(r'b>\s*' + self.section + r'\.(.+?)b>\s*' + self.next_section + r'\.', encoding='utf-8')
            p3 = bytes(r'' + self.section + r'\.\s*<\/b>(.+?)' + self.next_section + r'\.\s*<\/b>', encoding='utf-8')
            p4 = bytes(r'' + self.section + r'\.\s*[^<>]+\.\s*<\/b(.+?)' + self.next_section + r'\.\s*[^<>]+\.\s*<\/b',
                       encoding='utf-8')
            p5 = bytes(r'b>\s*<font[^>]+>\s*' + self.section + r'\.(.+?)b>\s*<font[^>]+>\s*' + self.next_section + r'\.', encoding='utf-8')
            p6 = bytes(r'' + self.section.upper() + r'\.\s*<\/b>(.+?)' + self.next_section.upper() + r'\.\s*<\/b>', encoding='utf-8')

            p7 = bytes(r'underline;\">\s*' + self.section + r'\<\/font>(.+?)underline;\">\s*'+ self.next_section + r'\.\s*\<\/font>',encoding = 'utf-8')
            p8 = bytes(r'underline;\">\s*' + self.section + r'\.\<\/font>(.+?)underline;\">\s*'+ self.next_section + r'\.\s*\<\/font>',encoding = 'utf-8')
            p9 = bytes(r'<font[^>]+>\s*' + self.section + r'\:(.+?)\<font[^>]+>\s*'+self.next_section + r'\:\s*',encoding = 'utf-8')
            p10 = bytes(r'<font[^>]+>\s*' + self.section + r'\.\<\/font>(.+?)\<font[^>]+>\s*' + self.next_section + r'\.',encoding = 'utf-8')
            p11 = bytes(r'' + self.section + r'\.(.+?)<font[^>]+>\s*' + self.next_section + r'\.\<\/font>',encoding = 'utf-8')
            p12 = bytes(r'b>\s*<font[^>]+>\s*' + self.section + r'(.+?)b>\s*<font[^>]+>\s*' + self.next_section + r'\s*\<\/font>', encoding='utf-8')
            p13 = bytes(r'' + self.section + r'\.\s*[^<>]+\.\s*<\/b(.+?)b>\s*' + self.next_section + r'\.',
                       encoding='utf-8')

            regexs = (
                p1,  # <===pattern 1: with an attribute bold before the item subtitle
                p2,  # <===pattern 2: with a tag <b> before the item subtitle
                p3,  # <===pattern 3: with a tag <\b> after the item subtitle
                p4,  # <===pattern 4: with a tag <\b> after the item+description subtitle
                p5,  # <===pattern 5: with a tag <b><font ...> before the item subtitle
                p6,  # <===pattern 6: with a tag <\b> after the item subtitle (ITEM XX.<\b>)
                p7,
                p8,
                p9,
                p10,
                p11,
                p12,
                p13,
                )

            # Now we try to see if a match can be found...
            for regex in regexs:
                match = re.search(regex, page,
                                  flags=re.IGNORECASE)  # <===search for the pattern in HTML using re.search from the re package. Ignore cases.

                # If a match exist....
                if match:
                    # Now we have the extracted content still in an HTML format
                    # We now turn it into a beautiful soup object
                    # so that we can remove the html tags and only keep the texts

                    soup = BeautifulSoup(match.group(1),
                                         "html.parser")  # <=== match.group(1) returns the texts inside the parentheses (.*?)

                    # soup.text removes the html tags and only keep the texts
                    rawText = soup.text.encode('utf8')  # <=== you have to change the encoding the unicodes

                    break  # <=== if a match is found, we break the for loop. Otherwise the for loop continues

        if match is None:
            print(f'No matched sections: {self.section}, {self.next_section} found in {input_path}.')
            return None
        else:
            return rawText

    @property
    def range(self):
        return generate_key(self.section, self.next_section)

def main(sections, amount=2):  
    paths = find_filings_paths()

    amount = len(paths) if amount > len(paths) else amount

    results = {
        "paths": [],
    }

    for start, end in sections:
        results[generate_key(start, end)] = []
    
    scrapers = [TenKScraper(start, end) for start, end in sections]

    for idx, path in enumerate(paths[:amount]):
        results["paths"].append(path)
        
        for scraper in scrapers:
            items = scraper.scrape(path)
            results[scraper.range].append(items)

        print(f"Scraping {path} - {idx + 1}/{len(paths)}.")
    return results
    
if __name__ == "__main__":
    sections = [('Item 1A', 'Item 1B'), ('Item 7', 'Item 7A')]
    results = main(sections, 100)
    df = pd.DataFrame(results)
    df.to_csv("./scrape_results/19-10k-item1A-item7.csv")
