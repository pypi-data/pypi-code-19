import argparse
import time
import os
from BlackBoxAuditing.find_contexts.find_cn2_rules import CN2_learner
from BlackBoxAuditing.find_contexts.expand_and_find_contexts import expand_and_find_contexts

def find_contexts(auditor, removed_attr, output_dir, beam_width=10, min_covered_examples=1, max_rule_length=5, by_original=True, epsilon=0.05):
   

    # Create directory to dump results
    if not os.path.exists(output_dir):
      os.makedirs(output_dir)

    # retrive data from the audit
    audits_data = self._audits_data
    orig_train = audits_data["train"]
    orig_test = audits_data["test"]
    obscured_test_data = audits_data["rep_test"][removed_attr]
    headers = audits_data["headers"]
    response_header = audits_data["response"]
    features_to_ignore = audits_data["ignore"]
    correct_types = audits_data["types"]
    obscured_tag = "-no"+removed_attr

    # Extract influence scores
    ranks = audits_data["ranks"]
    influence_scores = {}
    for element in ranks:
      influence_scores[element[0]] = float(element[1])
      influence_scores[element[0]+obscured_tag] = 0.0

    # Get obscured data from file:
    obscured_test = []
    obscured_test_reader = csv.reader(open(obscured_test_data, 'r'))
    for row in obscured_test_reader:
      obscured_test.append(row)

    # load data from audit to prepare it for context finding process
    audit_params = (orig_train, orig_test, obscured_test, headers, response_header, features_to_ignore, correct_types, obscured_tag)

    orig_train_tab, orig_test_tab, merged_data = load(audit_params, output_dir)

    # run the context_finder 
    context_finder(orig_train, orig_test, obscured_test, orig_train_tab, orig_test_tab, merged_data, obscured_tag, output_dir, influence_scores, beam_width, min_covered_examples, max_rule_length, by_original, epsilon)


def context_finder(orig_train, orig_test, obscured_train, orig_train_tab, orig_test_tab, merged_data, obscured_tag, output_dir, influence_scores, beam_width, min_covered_examples, max_rule_length, by_original, epsilon):
  # Generate rule list for the original data using the CN2 algorithm
  rulesfile, accuracy, AUC = CN2_learner(orig_train_tab, orig_test_tab, output_dir, beam_width, min_covered_examples, max_rule_length, influence_scores)

  # Generate fully expanded rule list, store best expanded rule for each of the original rules,
  # and return contexts of discrimination
  contexts_of_influence = expand_and_find_contexts(orig_train, obscured_train, merged_data, rulesfile, influence_scores, obscured_tag, output_dir, by_original, epsilon)

  parsed_contexts = []
  for outcome in contexts_of_influence:
    list_of_contexts = contexts_of_influence[outcome]
    contexts = '\t'+" OR \n\t".join([" AND ".join(context) for context in list_of_contexts])
    parsed_contexts.append((outcome, contexts))

  # Store summary results:
  summary_info = ["\nCN2 Settings Used:",
                  "rules found for {}".format(orig_train_tab),
                  "beam_width: {}".format(beam_width),
                  "min_covered_examples: {}".format(min_covered_examples),
                  "max_rule_length: {}\n".format(max_rule_length),
                  "CN2 Model Evaluation:",
                  "Model tested on {}".format(orig_test_tab),
                  "Accuracy: {}".format(accuracy),
                  "AUC: {}\n".format(AUC)]

  # Print summary results
  for info_line in summary_info:
    print(info_line)

   
  print("\nContexts of influence found:")
  for parsed_context in parsed_contexts:
    print(parsed_context[0])
    print(parsed_context[1]+'\n\n')

    
  # Write results to summary file:
  summary = "{}/contexts.summary".format(output_dir)
  summary_file = open(summary, 'w')

  for info_line in summary_info:
    summary_file.write(info_line+'\n')

  summary_file.write("Contexts of influence found:\n")
  for parsed_context in parsed_contexts:
    summary_file.write(parsed_context[0]+':\n')
    summary_file.write(parsed_context[1]+'\n\n')

  print("Summary of Experiment written to {}".format(summary))
