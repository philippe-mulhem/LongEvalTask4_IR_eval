# LongEvalTask4_IR_eval
The code for IR evaluation of Task 4 of LongEval 2026.

Usage:
    IR-eval.py --submission <submission_file.jsonl> --gold <groundtruth_file.jsonl> [--outdir <output directory>] [--help]


Description : the python code uses a correct submission_file.jsonl, the groundtruth file groundtruth_file.jsonl, and generates the IR part of task 4 in the standard ourput and optionally in a directory provided. The IR evaluation of the task is a simple precision@Qk, meaning that we evaluate the precision according to the number of retrieved documents for a query Qk that were used for the generation part. We compute the precision with respect to the retrieved documents, because we assume that the submission indicates the documents that are used.
