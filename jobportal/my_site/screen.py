import warnings
import textract
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.neighbors import NearestNeighbors
import PyPDF2
import pathlib
from json import load, dumps
from operator import getitem
from collections import OrderedDict, defaultdict
from datetime import datetime, date
from dateutil import relativedelta
from typing import Dict, List
from .text_process import normalize

import nltk
from nltk.tokenize import word_tokenize
from my_site.configurations import regex

warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
nltk.download('punkt')

def get_file_path(loc: pathlib.Path) -> str:
    return str(loc).replace('\\', '/')

def get_file_name(filename: str) -> str:
    return filename.rsplit('\\')[1]

def read_result_in_json(jobfile: str = 'job1') -> Dict:
    filepath = 'result/'
    with open(f'{filepath}{jobfile}.json', 'r') as openfile:
        result = load(openfile)
    return result

def write_result_in_json(data: Dict, jobfile: str = 'job1') -> None:
    filepath = 'result/'
    json_str = dumps(data, indent=4)
    with open(f'{filepath}{jobfile}.json', 'w+', encoding='utf-8') as f:
        f.write(json_str)

def get_number_of_months(datepair: Dict) -> int:
    try:
        present_vocab = {"present", "date", "now"}
        gap = datepair.get("fh", "")
        
        date1_key, date2_key = "fyear", "syear"

        if "smonth_num" in datepair:
            date1_key, date2_key = "fmonth_num", "smonth_num"
        elif "smonth" in datepair:
            date1_key, date2_key = "fmonth", "smonth"

        date1, date2 = datetime.strptime(str(datepair[date1_key]), "%Y"), datepair[date2_key]
        date2 = datetime.now() if date2.lower() in present_vocab else datetime.strptime(str(date2), "%Y")
        
        months_of_experience = relativedelta.relativedelta(date2, date1)
        return months_of_experience.years * 12 + months_of_experience.months

    except Exception as e:
        return 0

def get_total_experience(experience_list: List) -> int:
    return sum(get_number_of_months(i) for i in experience_list)

def calculate_experience(resume_text: str) -> int:
    def get_month_index(month: str) -> int:
        month_dict = {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6, 'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12}
        return month_dict[month.lower()]

    try:
        start_month, start_year, end_month, end_year = -1, -1, -1, -1
        regular_expression = re.compile(regex.date_range, re.IGNORECASE)
        regex_result = re.search(regular_expression, resume_text)
        
        while regex_result:
            date_range = regex_result.group()
            year_regex = re.compile(regex.year)
            year_result = re.search(year_regex, date_range)

            if start_year == -1 or int(year_result.group()) <= start_year:
                start_year = int(year_result.group())
                month_regex = re.compile(regex.months_short, re.IGNORECASE)
                month_result = re.search(month_regex, date_range)

                if month_result:
                    current_month = get_month_index(month_result.group())
                    start_month = min(start_month, current_month) if start_month != -1 else current_month

            if 'present' in date_range.lower():
                end_month, end_year = date.today().month, date.today().year
            else:
                year_result = re.search(year_regex, date_range[year_result.end():])

                if end_year == -1 or int(year_result.group()) >= end_year:
                    end_year = int(year_result.group())
                    month_regex = re.compile(regex.months_short, re.IGNORECASE)
                    month_result = re.search(month_regex, date_range)

                    if month_result:
                        current_month = get_month_index(month_result.group())
                        end_month = max(end_month, current_month) if end_month != -1 else current_month

            resume_text = resume_text[regex_result.end():]
            regex_result = re.search(regular_expression, resume_text)

        return end_year - start_year if end_year != -1 else None

    except Exception as e:
        print('Issue calculating experience:', e)
        return None

def get_experience_year(job_expr):
    job_expr = str.split(job_expr, ' ')[0]
    if '-' in job_expr:
        expr = job_expr.split('-')
        return int(expr[0])*12, int(expr[1])*12
    return int(job_expr)*12, -1


# for 2nd method
def getTotalExperienceFormatted(exp_list, job_expr) -> bool:

    min_yr_in_month, max_yr_in_month = get_experience_year(job_expr)
    print(min_yr_in_month, max_yr_in_month)
    print(exp_list)
    months = get_experience_year(exp_list)

    if max_yr_in_month != -1:
        if (months >= min_yr_in_month) and (months <= max_yr_in_month):
            return True
    else:
        if months >= min_yr_in_month:
            return True
    return False


def findWorkAndEducation(text, name) -> Dict[str, List[str]]:
    categories = {"Work": ["(Work|WORK)", "(Experience(s?)|EXPERIENCE(S?))", "(History|HISTORY)"]}
    inv_data = {v[0][1]: (v[0][0], k) for k, v in categories.items()}
    line_count = 0
    exp_list = defaultdict(list)
    name = name.lower()

    current_line = None
    is_dot = False
    is_space = True
    continuation_sent = []
    first_line = None
    unique_char_regex = "[^\sA-Za-z0-9\.\/\(\)\,\-\|]+"

    for line in text.split("\n"):
        line = re.sub(r"\s+", " ", line).strip()
        match = re.search(r"^.*:", line)
        if match:
            line = line[match.end():].strip()

        # get first non-space line for filtering since
        # sometimes it might be a page header
        if line and first_line is None:
            first_line = line

        # update line_countfirst since there are `continue`s below
        line_count += 1
        if (line_count - 1) in inv_data:
            current_line = inv_data[line_count - 1][1]
        # contains a full-blown state-machine for filtering stuff
        elif current_line == "Work":
            if line:
                # if name is inside, skip
                if name == line:
                    continue
                # if like first line of resume, skip
                if line == first_line:
                    continue
                # check if it's not a list with some unique character as list bullet
                has_dot = re.findall(unique_char_regex, line[:5])
                # if last paragraph is a list item
                if is_dot:
                    # if this paragraph is not a list item and the previous line is a space
                    if not has_dot and is_space:
                        if line[0].isupper() or re.findall(r"^\d+\.", line[:5]):
                            exp_list[current_line].append(line)
                            is_dot = False

                else:
                    if not has_dot and (
                        line[0].isupper() or re.findall(r"^\d+\.", line[:5])
                    ):
                        exp_list[current_line].append(line)
                        is_dot = False
                if has_dot:
                    is_dot = True
                is_space = False
            else:
                is_space = True
        elif current_line == "Education":
            if line:
                # if not like first line
                if line == first_line:
                    continue
                line = re.sub(unique_char_regex, '', line[:5]) + line[5:]
                if len(line) < 12:
                    continuation_sent.append(line)
                else:
                    if continuation_sent:
                        continuation_sent.append(line)
                        line = " ".join(continuation_sent)
                        continuation_sent = []
                    exp_list[current_line].append(line)

    return exp_list


def check_basicRequirement(resumes_data, job_data):
    # print(job_experience)
    Ordered_list_Resume = []
    Resumes = []
    Temp_pdf = []
    # print(int(job_data.experience.split(' ')[0].split('-')[0]))
    # print(len(resumes_data))
    # filter resumes based on the gender
    resumes_data = resumes_data.filter(experience__gte=float(job_data.experience.split(' ')[0].split('-')[0]))
    print(len(resumes_data))
    if job_data.gender == 'Male':
        resumes_data = resumes_data.filter(gender='Male')
    elif job_data.gender == 'Female':
        resumes_data = resumes_data.filter(gender='Female')

    # resumes file path
    filepath = 'media/'
    resumes = [str(item.cv) for item in resumes_data]
    print("resumes: ", resumes)
    resumes_new = [item.split(':')[0] for item in resumes]
    resumes_new = [item for item in resumes_new if item != '']

    LIST_OF_FILES = resumes_new

    print("Total Files to Parse\t", len(LIST_OF_FILES))
    print("####### PARSING ########")
    for indx, file in enumerate(LIST_OF_FILES):
        print(indx, file)
        if not pathlib.Path(filepath+file).is_file():
            continue
        Ordered_list_Resume.append(file)

        Temp = file.split('.')
        print(Temp)

        if Temp[1] == "pdf" or Temp[1] == "Pdf" or Temp[1] == "PDF":
            try:
                # print("This is PDF", indx)
                with open(filepath + file, 'rb') as pdf_file:
                    # read_pdf = PyPDF2.PdfFileReader(pdf_file)

                    read_pdf = PyPDF2.PdfReader(pdf_file, strict=False)
                    # print("resume", indx,": ", read_pdf)
                    number_of_pages = len(read_pdf.pages)
                    for page_number in range(number_of_pages):
                        page = read_pdf.pages[page_number]
                        page_content = page.extract_text()
                        # print(page_content)
                        page_content = page_content.replace('\n', ' ').replace('\f', '').replace('\\uf[0-9]+',
                                                                                                 '').replace(
                            '\\u[0-9]+', '').replace('\\ufb[0-9]+', '')
                        # page_content.replace("\r", "")

                        Temp_pdf = str(Temp_pdf) + str(page_content)

                        # print(Temp_pdf)

                        Resumes.extend([Temp_pdf])

                    # if getTotalExperienceFormatted(Temp_pdf,  job_data.experience):
                    #     Resumes.extend([Temp_pdf])

                    Temp_pdf = ''

                    # f = open(str(i)+str("+") , 'w')
                    # f.write(page_content)
                    # f.close()
            except Exception as e:
                print(e)

        if Temp[1] == "doc" or Temp[1] == "Doc" or Temp[1] == "DOC":
            # print("This is DOC", file)

            try:
                a = textract.process(filepath)
                a = a.replace(b'\n', b' ')
                a = a.replace(b'\r', b' ')
                b = str(a)
                c = [b]
                Resumes.extend(c)
            except Exception as e:
                print(e)

        if Temp[1] == "docx" or Temp[1] == "Docx" or Temp[1] == "DOCX":
            # print("This is DOCX", file)
            try:
                a = textract.process(filepath + file)
                a = a.replace(b'\n', b' ')
                a = a.replace(b'\r', b' ')
                b = str(a)
                c = [b]
                Resumes.extend(c)
            except Exception as e:
                print(e)

        if Temp[1] == "exe" or Temp[1] == "Exe" or Temp[1] == "EXE":
            # print("This is EXE", file)
            pass
    print("Done Parsing.")
    return Resumes, Ordered_list_Resume


def get_rank(result_dict=None):

    if result_dict == None:
        return {}

    # new_result_dict = sorted(result_dict.items(), key=lambda item: float(item[1]["score"]), reverse=False)
    new_result_dict = OrderedDict(sorted(result_dict.items(), key=lambda item: getitem(item[1], 'score'), reverse=False))
    new_updated_result_dict = {}
    indx = 0
    for _, item in new_result_dict.items():
        item['rank'] = indx + 1
        new_updated_result_dict[indx] = item
        indx += 1
    return new_updated_result_dict


def show_rank(result_dict=None, jobfileName='job1', top_k=20):
    if (result_dict == None):
        filepath = 'result/' + jobfileName + '.json'
        result_dict = read_result_in_json(filepath)
    print("\nResult:")
    for _, result in result_dict.items():
        # print(result)
        print(f"Rank: {result['rank']}\t Total Score:{round(result['score'], 5)} (NN distance) \tName:{result['name']}")


# start parsing
# result
def res(resumes_data, job_data):
    result_arr = dict()
    print("Resumes: ", resumes_data.values('cv'))

    # checking basic requirements
    Resumes, Ordered_list_Resume = check_basicRequirement(resumes_data, job_data)

    if not Ordered_list_Resume or not Resumes:
        return result_arr

    # job-description
    Job_Desc = 0
    job_desc_filepath = 'jobDetails/'
    jobfilename = job_data.company_name + '_' + job_data.title + '.txt'
    job_desc = job_data.details + '\n' + job_data.responsibilities + '\n' + job_data.experience + '\n';
    job_desc = re.sub(r' +', ' ', job_desc.replace('\n', '').replace('\r', ''))

    try:
        text = re.sub(' +', ' ', job_desc)
        tttt = str(text)
        tttt = normalize(word_tokenize(tttt))
        print(tttt)
        text = [' '.join(tttt)]
    except:
        text = 'None'
    print("\nNormalized Job Description:\n", text)

    # get tf-idf of Job Description
    vectorizer = CountVectorizer(stop_words='english')
    transformar = TfidfTransformer()
    vectorizer.fit(text)
    vector = transformar.fit_transform(vectorizer.transform(text).toarray())
    Job_Desc = vector.toarray()
    print("\nTF-IDF weight  (For Job Description):\n", Job_Desc, '\n')

    # get TF-IDF of Candidate Resumes
    Resume_Vector = []
    for file in Resumes:
        text = file
        tttt = str(text)
        try:

            tttt = normalize(word_tokenize(tttt))
            text = [' '.join(tttt)]
            print("Normalized resume: ", text)

            vector = transformar.fit_transform(vectorizer.transform(text).toarray())

            aaa = vector.toarray()
            print("TF-IDF weight(For Resumes): \n", aaa)
            Resume_Vector.append(aaa)
        except:
            pass

    # ranking process

    for indx, file in enumerate(Resume_Vector):
        samples = file
        name = Ordered_list_Resume[indx]
        neigh = NearestNeighbors(n_neighbors=1)
        neigh.fit(samples)
        NearestNeighbors(algorithm='auto', leaf_size=30)

        # score = round(neigh.kneighbors(Job_Desc)[0][0][0], 5)
        score = neigh.kneighbors(Job_Desc)[0][0][0]
        # print(score)
        result_arr[indx] = {'name': name, 'score': score}

    result_arr = get_rank(result_arr)
    show_rank(result_arr, jobfilename)

    # return resultant shortlist
    return result_arr
