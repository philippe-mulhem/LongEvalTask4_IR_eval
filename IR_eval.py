#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

"""
Module: Computing of the precision at Q-length for the LongEval 2026 Task 4
Description:
    Load one valid submission run and one groundtruth file
    Keep the relevant information for the computation of the precision at Q-lenght
    Computes and prints (on standard output) the per query and averaged precision at Q-length

Usage:
    IR-eval.py --submission <submission_file.jsonl> --gold <groundtruth_file.jsonl> [--outdir <output directory>] [--help]

Dependencies:
    - None

Notes:
    - The reading of the files supposes an utf-8 coding, this may be not valid for runs from Asia for instance...
    - The output file name is <team_id>-<run_id>_prec.txt
    
Author: Philippe Mulhem
Email: Philippe.Mulhem@imag.fr
Affiliation: MRIM-LIG, Centre National de la Recherche Scientifique
License: MIT
Version 1.0.3  (adding the process of several answers fr one query)
Version: 1.0.2 (modifs arg processing et text file save)
Date: 2024-05-07
Contributors: /
GitHub: /
"""

# Standard library imports
import json
import sys

import argparse
from pathlib import Path

############################################################
#      Generic functions
############################################################

def load_jsonl_file(file_path,req_keys):
    """Reads a jsonl file.
    Args:
        file_path (string): jsonl filename
    Returns:
        type: a data varaiale that contains the structures of the json file.
    Raises:
        Error in the opening or reading of the file : FileNotFoundError, PermissionError, UnicodeDecodeError, OSError
    Note:
        Read line by line.
    """
    data = [] # init
    lnumber=1
    try:
        with open(file_path, 'r', encoding='utf-8') as file: # NOTE : may be utf-8 encoding to be modified...
            for line in file: # read by line
                entry = json.loads(line)
                #print(entry.keys())
                missing_keys = req_keys - set(entry.keys())
                if missing_keys:
                    print(f"Line: {lnumber} - Fields Expected: {missing_keys}. Exit.")
                    sys.exit(1)
                data.append(entry)
                lnumber += 1
    except FileNotFoundError as e:
        raise FileNotFoundError(f"The file '{file_path}' is not found.") from e
    except PermissionError as e:
        raise PermissionError(f"Permission non granted to read the file '{file_path}'.") from e
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            f"Encoding error in the file '{file_path}'. Vérify that the file in in UTF-8."
        ) from e
    except OSError as e:
        raise OSError(f"Systerm error when opening the file '{file_path}': {e}") from e
    return data

############################################################
#      Processing of the submission file
############################################################
# Path to submission file in arg 1
submission_file_path = sys.argv[1]

# simple test on the top-fields that must be present for a submission file
required_submission_keys = {"metadata", "answer", "references"}

# Variable that stores the submission file content
#submission_data = load_jsonl_file(submission_file_path)

# variables for team and run names
team_id = ""
run_id = ""

# variables for the precision computations
# the citations references (docids) retrieved in the run, per query
submission_data_for_prec = {}

def process_submission(data):
    """Processes a variable that contains the content of the submission file.
    Args:
        data : the variable with the file content. It's type is
            metadata
                team_id (text)
                run_id  (text)
                narrative_id  (integer)
            answer
                list of
                    text   (text)
                    citations
                        list of
                            (text)
            references
                list of
                    (text)
    Returns:
        [query_id][list of doc_id:1 ]: The list (dictionary) of retrieved documents per query (query_id).
    Raises:
        None
    Note:
        As the submission file does contain the position in the doc_id list, we need to find them back.
    """
    global team_id
    global run_id
    cit_id = {}
    for entry in data:
        team_id = entry['metadata']['team_id']
        run_id = entry['metadata']['run_id']
        qid = entry['metadata']['narrative_id']
        answer = entry['answer'][0]['text']
        #citations = entry['answer'][0]['citations'] # old version, assuming ONE answer
        citations = []      # v2 assuming several answers
        for answ in entry['answer']:
            citations.extend(answ['citations'])
        refs = entry['references']
        cit_id[qid] = {}
        for i in citations:
            cit_id[qid][str(refs[i])] = 1
    return(cit_id)


def get_submission(submission_file_path, submission_keys):
    """Returns the submission data needed for the evaluation from the input file and the needed fields.
    Args:
        file_path (string): jsonl file name
        submission_keys : the mandatory top-level keys needed
    Returns:
        type: a data that contains the structures needed.
    Raises:
        Catcheds Error in the opening or reading of the file, and in case of problem with fields
    Note:
        Simple calls.
    """
    sub_data = {}
    try:
        submission_data = load_jsonl_file(submission_file_path,submission_keys)
        sub_final = process_submission(submission_data)
    except Exception as e:
        print(f"!!! {e} !!!", file=sys.stderr)
        print("Exit.")
        sys.exit(1)
    return sub_final

# Test call to get the submission structure
#submission_data_for_prec=get_submission(sys.argv[1], required_submission_keys)

############################################################
#      Processing of the groundtruth (Qrel) file
############################################################


# simple test on the top-fields that must be present for a groundtruth file
required_groundtruth_keys = {"query_id", "paper_1_id", "paper_1_title", "paper_2_id", "paper_2_title", "paper_1_publishedDate", "paper_2_publishedDate", "relation_type", "confidence", "bridge_concept", "question", "answer", "reasoning_path"}

def process_groundtruth(data):
    """Processes a variable that contains the content of the groundtruth file.
    Args:
        data : the variable with the file content. It's type is
            query_id (text)
            paper_1_id (text)
            paper_1_title (text)
            paper_2_id (text)
            paper_2_title (text)
            paper_1_publishedDate (text)
            paper_2_publishedDate (text)
            relation_type (text)
            confidence (float)
            bridge_topic (text)
            question (text)
            hop1_fact (text)
            hop2_fact (text)
            answer (text)
            reasoning_path (text)
    Returns:
        [query_id][list of doc_id:1 ]: The list (dictionary) of relevant documents per query (query_id).
    Raises:
        None
    Note:
        Simple calls.
    """
    result = {}
    for entry in data:
        query_id = entry['query_id']
        result[query_id] = {
            entry['paper_1_id']: 1,
            entry['paper_2_id']: 1
        }
    return result


def get_groundtruth(groundtruth_file_path, groundtruth_keys):
    """Returns the groundtruth data needed for the evaluation from the input file and the needed fields.
    Args:
        file_path (string): jsonl groudtruth file name
        submission_keys : the mandatory top-level keys needed
    Returns:
        type: a data that contains the structures needed.
    Raises:
        Catcheds Error in the opening or reading of the file, and in case of problem with fields
    Note:
        Simple calls.
    """
    gt_final = {}
    try:
        groundtruth_data = load_jsonl_file(groundtruth_file_path,groundtruth_keys)
        gt_final = process_groundtruth(groundtruth_data)
    except Exception as e:
        print(f"!!! {e} !!!", file=sys.stderr)
        print("Exit.")
        sys.exit(1)
    return gt_final

# Test call to get the groundtruth structure
# groundtruth_data_for_prec=get_groundtruth(sys.argv[2], required_groundtruth_keys)


############################################################
#      Processing of the precision at Q-length and print
############################################################

def compute_and_save_prec_scores (gt_data, sub_data, out_dirname):
    """Computes and prints the precision per query and averages for one run.
    Args:
        gt_data (dicionary): the data extracted from the groundtruth file
        sub_data (dicionary) : the data extracted from the submission file
    Returns:
        None
    Raises:
        None. It cathes the exceptions related to creation of dir and file saving
    Note:
        Two steps : per query and then averaged.
        Is displays to standard output also, so that we can check that things are going ok.
    """

    global team_id
    global run_id
    
    p_at_q = {} # storage of the eval per query

    #step 1 : precision per query = how many retrieved are relevant / retrieved size
    for qid, docs in gt_data.items():
        if qid in sub_data:
            count_rel = 0 # count of relevant found
            for doc in docs:
                if doc in sub_data[qid]: # if one relevant doc in retrieved
                    count_rel +=1
            nb_ret= len(sub_data[qid]) # size of retrieved
            if nb_ret != 0:
                p_at_q[qid] = count_rel/nb_ret
            else:
                p_at_q[qid] = 0.0 # when no retrieved doc precision = 0.0
        else: # we count 0.0 if no answer for one query
            p_at_q[qid] = 0.0
        print(team_id," ",run_id," ",qid,": ",format(p_at_q[qid], ".4f")) # print
    
    # step 2 : averaging
    p_at_q_avg = 0.0 # average
    for q in p_at_q:
        p_at_q_avg +=p_at_q[q]
    p_at_q_avg = p_at_q_avg / float(len(gt_data)) # hypothesis : more than 0 relevant doc
    print(team_id," ",run_id," avg_prec_at_q: ",format(p_at_q_avg, ".4f")) # print

    # saving
    try:
        outdir = Path(out_dirname)
        outdir.mkdir(parents=True, exist_ok=True)
        txt_path = outdir / f"{team_id}_{run_id}_prec.txt"
        with txt_path.open("w", encoding="utf-8") as f:
            for qid in p_at_q:
                f.write(f"{team_id} {run_id} {qid}: {p_at_q[qid]:.4f}\n") # print per query
            f.write(f"{team_id} {run_id} avg_prec_at_q: {p_at_q_avg:.4f}") # print average
    except Exception as e:
        print(f"!!! Cannot save evaluation file: {e} !!!", file=sys.stderr)
        print("Exit.")
        sys.exit(1)
        
# Test call to get the evaluation print
#compute_and_print_prec_scores(groundtruth_data_for_prec, submission_data_for_prec)

############################################################
#      main
############################################################
def main(req_sub_keys, gt_req_keys):
    """Loads data files and computes precision for one run.
    Args:
        sub_filename (str): submission file name
        req_sub_keys ([str]) : list of required submission fields
        sgt_filename (str): groundtruth file name
        gt_sub_keys ([str]) : list of required groundtruth fields
    Returns:
        None
    Raises:
        None
    Note:
        Call the reading of submission and groundtruth files, and print precision
    """
    #command line parsing
    parser = argparse.ArgumentParser(
        description="Evaluate CLEF LongEval-RAG Task 4 submissions precision at lenght of Q, per qury and averaged."
    )
    parser.add_argument("--submission",      required=True,                help="Participant submission JSONL file.")
    parser.add_argument("--gold",            required=True,                help="Gold standard JSONL file.")
    parser.add_argument("--outdir",          default="evaluation_outputs", help="Output directory (created if not existing).")
    args = parser.parse_args()
    # the processing calls
    submission_data_for_prec=get_submission(args.submission, req_sub_keys) # load submission
    # print(submission_data_for_prec)
    groundtruth_data_for_prec=get_groundtruth(args.gold, gt_req_keys) #load groundtruth
    compute_and_save_prec_scores(groundtruth_data_for_prec, submission_data_for_prec,args.outdir) #processing and save

if __name__ == "__main__":
    main(required_submission_keys,required_groundtruth_keys)
